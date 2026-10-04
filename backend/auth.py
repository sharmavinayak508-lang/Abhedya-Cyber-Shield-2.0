import sqlite3
import hashlib
import os
from backend.database import DB_PATH

def hash_password(password, salt=None):
    """Hashes password using SHA-256 with salt."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(stored_password_hash, provided_password):
    """Verifies a stored password against provided input."""
    if ":" not in stored_password_hash:
        return False
    salt, hashed = stored_password_hash.split(":", 1)
    recalculated = hashlib.sha256((salt + provided_password).encode('utf-8')).hexdigest()
    return recalculated == hashed

def ensure_default_user():
    """Forces the default 'admin' user with password 'admin' to exist in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    pwd_hash = hash_password("admin")
    
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, status) VALUES (?, ?, ?, ?)",
            ("admin", pwd_hash, "admin", "approved")
        )
    else:
        cursor.execute(
            "UPDATE users SET password_hash = ?, role = 'admin', status = 'approved' WHERE username = 'admin'",
            (pwd_hash,)
        )
        
    conn.commit()
    conn.close()

def register_user(username, password):
    """Registers a new user pending approval."""
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    pwd_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role, status) VALUES (?, ?, ?, ?)",
        (username, pwd_hash, "user", "pending")
    )
    conn.commit()
    conn.close()
    return True, "Registration submitted! Pending admin verification."

class LoginGuard:
    def attempt(self, username, password):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT username, password_hash, role, status, theme FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return "error", "Invalid credentials.", None

        db_user, db_hash, db_role, db_status, db_theme = row

        if not verify_password(db_hash, password):
            return "error", "Invalid credentials.", None

        if db_status != "approved":
            return "error", f"Account status is '{db_status}'. Awaiting admin approval.", None

        user_data = {
            "username": db_user,
            "role": db_role,
            "status": db_status,
            "theme": db_theme or "Dark Cyber"
        }
        return "ok", "Login successful.", user_data
