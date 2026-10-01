"""Backend unit tests. Run from the project root:  python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402
from backend import (auth, crypto, database, file_tools, integrity,  # noqa: E402
                     logger, password_tools, rsa_demo, security_score)


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self._old = dict(PATHS)
        self._tmp = tempfile.TemporaryDirectory()
        root = self._tmp.name
        PATHS.update(
            data=root,
            vault_dir=os.path.join(root, "vault"),
            export_dir=os.path.join(root, "exports"),
            db=os.path.join(root, "test.db"),
            honeytoken=os.path.join(root, "canary.json"),
            vault_salt=os.path.join(root, "vault.salt"),
            vault_check=os.path.join(root, "vault.check"),
        )
        database.init_database()
        security_score.reset()
        crypto.lock_vault()
        while not logger.telemetry_queue.empty():
            logger.telemetry_queue.get_nowait()

    def tearDown(self):
        PATHS.update(self._old)
        self._tmp.cleanup()

    def write(self, name, data=b"hello"):
        path = os.path.join(self._tmp.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path


class TestPasswords(BackendTestCase):
    def test_weak_and_common(self):
        self.assertEqual(password_tools.analyze_password("abc")["level"], "critical")
        self.assertEqual(password_tools.analyze_password("password")["score"], 0)

    def test_strong(self):
        self.assertEqual(password_tools.analyze_password("Tr0ub4dor&3-horse-staple!")["level"], "strong")

    def test_generator_has_all_classes(self):
        for _ in range(50):
            pw = password_tools.generate_password(16)
            self.assertEqual(len(pw), 16)
            self.assertEqual(password_tools.analyze_password(pw)["level"], "strong")

    def test_generator_clamps_length(self):
        self.assertEqual(len(password_tools.generate_password(2)), 12)
        self.assertEqual(len(password_tools.generate_password(500)), 64)


class TestAuth(BackendTestCase):
    def test_default_user_and_verify(self):
        auth.ensure_default_user()
        self.assertTrue(auth.verify(auth.DEFAULT_USER, auth.DEFAULT_PASSWORD))
        self.assertFalse(auth.verify(auth.DEFAULT_USER, "wrong"))
        self.assertFalse(auth.verify("nobody", "x"))

    def test_password_is_not_stored_plain(self):
        auth.ensure_default_user()
        row = database.get_user(auth.DEFAULT_USER)
        self.assertNotIn(auth.DEFAULT_PASSWORD, str(row))

    def test_change_password(self):
        auth.ensure_default_user()
        self.assertFalse(auth.change_password("admin", "bad", "NewPass123!")[0])
        self.assertFalse(auth.change_password("admin", auth.DEFAULT_PASSWORD, "short")[0])
        self.assertTrue(auth.change_password("admin", auth.DEFAULT_PASSWORD, "NewPass123!")[0])
        self.assertTrue(auth.verify("admin", "NewPass123!"))

    def test_lockout(self):
        auth.ensure_default_user()
        guard = auth.LoginGuard(max_attempts=3, lock_seconds=30)
        self.assertEqual(guard.attempt("admin", "x")[0], "fail")
        self.assertEqual(guard.attempt("admin", "x")[0], "fail")
        self.assertEqual(guard.attempt("admin", "x")[0], "locked")
        self.assertEqual(guard.attempt("admin", auth.DEFAULT_PASSWORD)[0], "locked")
        guard.locked_until = 0
        self.assertEqual(guard.attempt("admin", auth.DEFAULT_PASSWORD)[0], "ok")


class TestFileTools(BackendTestCase):
    def test_hash_and_signature(self):
        demo = self.write("demo.txt", b"CYBERSHIELD-TEST-FILE")
        self.assertEqual(file_tools.scan_file(demo)["threat"], "CyberShield-Demo-Test-File")
        clean = self.write("clean.txt", b"just a normal file")
        self.assertIsNone(file_tools.scan_file(clean)["threat"])

    def test_empty_file_is_not_flagged(self):
        empty = self.write("empty.txt", b"")
        self.assertIsNone(file_tools.scan_file(empty)["threat"])

    def test_shred_removes_file(self):
        path = self.write("secret.txt", b"A" * 5000)
        self.assertTrue(file_tools.shred_file(path))
        self.assertFalse(os.path.exists(path))

    def test_shred_overwrites_content(self):
        path = self.write("secret2.txt", b"A" * 4096)
        seen = {}
        real_remove = os.remove
        def spy(p):
            with open(p, "rb") as f:
                seen["data"] = f.read()
            real_remove(p)
        os.remove = spy
        try:
            file_tools.shred_file(path)
        finally:
            os.remove = real_remove
        self.assertEqual(len(seen["data"]), 4096)
        self.assertNotEqual(seen["data"], b"A" * 4096)

    @unittest.skipUnless(crypto.HAS_CRYPTO, "cryptography not installed")
    def test_quarantine_requires_unlocked_vault(self):
        path = self.write("bad.bin", b"payload")
        ok, _msg = file_tools.quarantine_file(path, "Test")
        self.assertFalse(ok)
        self.assertTrue(os.path.exists(path))  # untouched

    @unittest.skipUnless(crypto.HAS_CRYPTO, "cryptography not installed")
    def test_quarantine_and_restore_roundtrip(self):
        crypto.setup_vault("MasterPass123!")
        path = self.write("bad.bin", b"payload-bytes")
        ok, _msg = file_tools.quarantine_file(path, "Test")
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(path))
        listed = file_tools.list_quarantined()
        self.assertEqual(len(listed), 1)
        self.assertEqual(file_tools.original_name(listed[0][0]), "bad.bin")
        out = os.path.join(self._tmp.name, "restored")
        os.makedirs(out)
        ok, _msg = file_tools.restore_file(listed[0][0], out)
        self.assertTrue(ok)
        with open(os.path.join(out, "bad.bin"), "rb") as f:
            self.assertEqual(f.read(), b"payload-bytes")


@unittest.skipUnless(crypto.HAS_CRYPTO, "cryptography not installed")
class TestVault(BackendTestCase):
    def test_setup_unlock_lock(self):
        self.assertFalse(crypto.vault_exists())
        with self.assertRaises(ValueError):
            crypto.setup_vault("short")
        crypto.setup_vault("MasterPass123!")
        self.assertTrue(crypto.vault_exists() and crypto.is_unlocked())
        crypto.lock_vault()
        self.assertFalse(crypto.unlock_vault("wrong-password"))
        self.assertFalse(crypto.is_unlocked())
        self.assertTrue(crypto.unlock_vault("MasterPass123!"))
        token = crypto.encrypt_bytes(b"data")
        self.assertEqual(crypto.decrypt_bytes(token), b"data")

    def test_locked_vault_refuses(self):
        with self.assertRaises(PermissionError):
            crypto.encrypt_bytes(b"x")


class TestIntegrity(BackendTestCase):
    def test_detects_changes(self):
        folder = os.path.join(self._tmp.name, "watched")
        a = self.write("watched/a.txt", b"one")
        self.write("watched/sub/b.txt", b"two")
        self.assertEqual(integrity.create_baseline(folder), 2)
        self.assertEqual(integrity.scan(folder)["unchanged"], 2)

        with open(a, "wb") as f:
            f.write(b"CHANGED")
        os.remove(os.path.join(folder, "sub", "b.txt"))
        self.write("watched/c.txt", b"new")
        result = integrity.scan(folder)
        self.assertEqual(result["modified"], ["a.txt"])
        self.assertEqual(result["deleted"], [os.path.join("sub", "b.txt")])
        self.assertEqual(result["new"], ["c.txt"])

    def test_scan_without_baseline_raises(self):
        folder = os.path.join(self._tmp.name, "empty")
        os.makedirs(folder)
        with self.assertRaises(ValueError):
            integrity.scan(folder)


class TestScoreAndLogs(BackendTestCase):
    def test_score_drops_and_recovers(self):
        logger.log_event("x", "CRITICAL")
        self.assertEqual(security_score.get_score(), 85)
        security_score.recover(5)
        self.assertEqual(security_score.get_score(), 90)
        for _ in range(20):
            logger.log_event("x", "CRITICAL")
        self.assertEqual(security_score.get_score(), 0)
        self.assertEqual(security_score.get_label()[0], "CRITICAL")

    def test_logs_are_persisted_and_filterable(self):
        logger.log_event("alpha", "INFO")
        logger.log_event("beta problem", "ERROR")
        self.assertEqual(len(logger.drain_queue()), 2)
        self.assertEqual(len(database.fetch_logs()), 2)
        self.assertEqual(len(database.fetch_logs(severity="ERROR")), 1)
        self.assertEqual(len(database.fetch_logs(search="alpha")), 1)


class TestRsaDemo(BackendTestCase):
    def test_roundtrip(self):
        for _ in range(20):
            k = rsa_demo.generate_keys()
            cipher = rsa_demo.encrypt_text("Hello CyberShield!", k["e"], k["n"])
            self.assertEqual(rsa_demo.decrypt_text(cipher, k["d"], k["n"]), "Hello CyberShield!")


if __name__ == "__main__":
    unittest.main()
