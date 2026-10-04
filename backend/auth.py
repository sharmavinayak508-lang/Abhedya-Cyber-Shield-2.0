"""Salted PBKDF2 password storage and registration approval verification."""
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


def register_user(username, password, role="customer"):
    """Register a new user account (marked as pending approval)."""
    if database.get_user(username) is not None:
        return False, "Username already exists."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    salt = os.urandom(16)
    database.add_user(
        username=username,
        salt_hex=salt.hex(),
        hash_hex=_hash(password, salt).hex(),
        iterations=ITERATIONS,
        status="pending",
        role=role,
        theme="Dark Cyber",
    )
    return True, "Registration submitted. Pending admin verification."


def ensure_default_user():
    """Ensure standard admin user exists and is pre-approved."""
    if database.get_user(DEFAULT_USER) is None:
        salt = os.urandom(16)
        database.add_user(
            username=DEFAULT_USER,
            salt_hex=salt.hex(),
            hash_hex=_hash(DEFAULT_PASSWORD, salt).hex(),
            iterations=ITERATIONS,
            status="approved",
            role="admin",
            theme="Dark Cyber",
        )


def verify_user(username, password):
    """Verifies credentials AND checks if account is verified/approved by admin."""
    row = database.get_user(username)
    if row is None:
        _hash(password, b"\x00" * 16)  # Maintain timing match
        return False, "Invalid credentials.", None

    expected = bytes.fromhex(row["pw_hash"])
    actual = _hash(password, bytes.fromhex(row["salt"]), row["iterations"])
    
    if not hmac.compare_digest(expected, actual):
        return False, "Invalid credentials.", None

    # Verification checks
    if row["status"] == "pending":
        return False, "Your registration is pending admin approval.", None
    if row["status"] == "rejected":
        return False, "Your registration request was rejected.", None

    return True, "Access granted.", row


def change_password(username, old_password, new_password):
    """Returns (ok, message)."""
    ok, msg, user = verify_user(username, old_password)
    if not ok:
        return False, "Current password is incorrect."
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters."

    salt = os.urandom(16)
    database.add_user(
        username=username,
        salt_hex=salt.hex(),
        hash_hex=_hash(new_password, salt).hex(),
        iterations=ITERATIONS,
        status=user["status"],
        role=user["role"],
        theme=user.get("theme", "Dark Cyber"),
    )
    return True, "Password updated successfully."


class LoginGuard:
    """Locks the login form for a period after repeated failed attempts."""

    def __init__(self, max_attempts=3, lock_seconds=30):
        self.max_attempts = max_attempts
        self.lock_seconds = lock_seconds
        self.failures = 0
        self.locked_until = 0.0

    def seconds_locked(self):
        return max(0, int(self.locked_until - time.time() + 0.999))

    def attempt(self, username, password):
        """Returns (status, message, user_data). Status is 'ok', 'fail', or 'locked'."""
        if self.seconds_locked() > 0:
            return "locked", f"Locked. Try again in {self.seconds_locked()}s.", None
        
        ok, msg, user = verify_user(username, password)
        if ok:
            self.failures = 0
            return "ok", msg, user
        
        self.failures += 1
        if self.failures >= self.max_attempts:
            self.failures = 0
            self.locked_until = time.time() + self.lock_seconds
            return "locked", f"Too many failures. Locked for {self.lock_seconds}s.", None
        
        left = self.max_attempts - self.failures
        return "fail", f"{msg} Attempts remaining: {left}", None

