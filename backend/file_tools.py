"""Hashing, signature check, secure shredding, encrypted quarantine and restore."""
import datetime
import hashlib
import os
import re
import time

from backend import crypto, database
from backend.logger import log_event
from config import PATHS

# Known-bad hashes. EICAR is the industry-standard harmless antivirus test file.
# The second entry lets you demo detection safely: create a text file that
# contains exactly   CYBERSHIELD-TEST-FILE   (no newline) and scan it.
SIGNATURES = {
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": "EICAR-Test-File",
    hashlib.sha256(b"CYBERSHIELD-TEST-FILE").hexdigest(): "CyberShield-Demo-Test-File",
}
QUARANTINE_SUFFIX = ".quarantine.enc"


def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def check_signature(sha256):
    return SIGNATURES.get(sha256)


def scan_file(path):
    """Hash a file, remember it, compare with signatures. Returns a result dict."""
    sha = sha256_file(path)
    database.save_hash(path, sha, datetime.datetime.now().isoformat(timespec="seconds"))
    threat = check_signature(sha)
    if threat:
        log_event(f"Signature match [{threat}] in {os.path.basename(path)}", "WARN")
    else:
        log_event(f"Clean hash for {os.path.basename(path)}: {sha[:16]}...", "INFO")
    return {"sha256": sha, "size": os.path.getsize(path), "threat": threat}


def shred_file(path, passes=3):
    """Overwrite a file in place with random data, then delete it.

    Note: on SSDs and journaling file systems overwriting is best-effort.
    """
    try:
        size = os.path.getsize(path)
        with open(path, "r+b", buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                remaining = size
                while remaining > 0:
                    block = min(remaining, 1024 * 1024)
                    f.write(os.urandom(block))
                    remaining -= block
                f.flush()
                os.fsync(f.fileno())
        os.remove(path)
        return True
    except OSError:
        return False


def quarantine_file(path, threat):
    """Encrypt a file into the vault, verify it, then shred the original.

    Returns (ok, message). Refuses to touch the file unless the vault is unlocked.
    """
    if not crypto.HAS_CRYPTO:
        return False, "The 'cryptography' package is missing. File was NOT touched."
    if not crypto.is_unlocked():
        return False, "Vault is locked. Unlock it on the VAULT page first. File was NOT touched."
    try:
        with open(path, "rb") as f:
            raw = f.read()
        token = crypto.encrypt_bytes(raw)
        if crypto.decrypt_bytes(token) != raw:  # verify before destroying anything
            return False, "Verification failed. File was NOT touched."
        os.makedirs(PATHS["vault_dir"], exist_ok=True)
        name = f"{os.path.basename(path)}.{int(time.time())}{QUARANTINE_SUFFIX}"
        dest = os.path.join(PATHS["vault_dir"], name)
        with open(dest, "wb") as f:
            f.write(token)
        shredded = shred_file(path)
        log_event(f"Quarantined [{threat}]: {os.path.basename(path)}", "CRITICAL")
        note = "" if shredded else " (original could not be deleted)"
        return True, f"File encrypted into the vault{note}:\n{dest}"
    except Exception as exc:
        log_event(f"Quarantine failure: {exc}", "ERROR")
        return False, f"Quarantine failed: {exc}"


def list_quarantined():
    """Returns list of (filename, size_bytes, modified_text), newest first."""
    folder = PATHS["vault_dir"]
    if not os.path.isdir(folder):
        return []
    rows = []
    for name in os.listdir(folder):
        if name.endswith(QUARANTINE_SUFFIX):
            full = os.path.join(folder, name)
            stamp = datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M")
            rows.append((name, os.path.getsize(full), stamp))
    return sorted(rows, key=lambda r: r[2], reverse=True)


def original_name(vault_name):
    base = vault_name[: -len(QUARANTINE_SUFFIX)]
    return re.sub(r"\.\d{9,11}$", "", base)


def restore_file(vault_name, dest_dir):
    """Decrypt a quarantined file into dest_dir. Returns (ok, message)."""
    if not crypto.is_unlocked():
        return False, "Vault is locked."
    try:
        with open(os.path.join(PATHS["vault_dir"], vault_name), "rb") as f:
            raw = crypto.decrypt_bytes(f.read())
        target = os.path.join(dest_dir, original_name(vault_name))
        if os.path.exists(target):
            target += ".restored"
        with open(target, "wb") as f:
            f.write(raw)
        log_event(f"Restored from vault: {os.path.basename(target)}", "WARN")
        return True, f"Restored to:\n{target}"
    except Exception as exc:
        return False, f"Restore failed: {exc}"
