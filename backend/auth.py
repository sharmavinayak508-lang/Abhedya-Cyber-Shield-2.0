"""Salted PBKDF2 password storage and a lock-out guard for the login screen."""
import hashlib
import hmac
import os
import time

from backend import database

ITERATIONS = 200_000
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "Admin@123"


def _hash(password, salt, iterations=ITERATIONS):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def create_user(username, password):
    salt = os.urandom(16)
    database.add_user(username, salt.hex(), _hash(password, salt).hex(), ITERATIONS)


def ensure_default_user():
    if database.get_user(DEFAULT_USER) is None:
        create_user(DEFAULT_USER, DEFAULT_PASSWORD)


def verify(username, password):
    row = database.get_user(username)
    if row is None:
        _hash(password, b"\x00" * 16)  # keep timing similar for unknown users
        return False
    expected = bytes.fromhex(row["pw_hash"])
    actual = _hash(password, bytes.fromhex(row["salt"]), row["iterations"])
    return hmac.compare_digest(expected, actual)


def change_password(username, old_password, new_password):
    """Returns (ok, message)."""
    if not verify(username, old_password):
        return False, "Current password is incorrect."
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters."
    create_user(username, new_password)
    return True, "Password updated."


class LoginGuard:
    """Locks the login form for a while after too many failures."""

    def __init__(self, max_attempts=3, lock_seconds=30):
        self.max_attempts = max_attempts
        self.lock_seconds = lock_seconds
        self.failures = 0
        self.locked_until = 0.0

    def seconds_locked(self):
        return max(0, int(self.locked_until - time.time() + 0.999))

    def attempt(self, username, password):
        """Returns (status, message); status is 'ok', 'fail' or 'locked'."""
        if self.seconds_locked() > 0:
            return "locked", f"Locked. Try again in {self.seconds_locked()}s."
        if verify(username, password):
            self.failures = 0
            return "ok", "Access granted."
        self.failures += 1
        if self.failures >= self.max_attempts:
            self.failures = 0
            self.locked_until = time.time() + self.lock_seconds
            return "locked", f"Too many failures. Locked for {self.lock_seconds}s."
        left = self.max_attempts - self.failures
        return "fail", f"Invalid credentials. Attempts remaining: {left}"
