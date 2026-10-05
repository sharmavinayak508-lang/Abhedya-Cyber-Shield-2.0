import sqlite3
import hashlib
import os

# --- DATABASE CONFIG ---
DB_PATH = os.path.join("data", "cybershield.db")

def _get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Ensure users table exists
def _init_auth_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'approved'
        )
    """)
    # Seed default admin account if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass_hash = _hash_password("admin")
        cursor.execute(
            "INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)",
            ("admin", admin_pass_hash, "admin", "approved")
        )
    conn.commit()
    conn.close()

# Initialize table on import
_init_auth_db()


# ==========================================
# AUTHENTICATION FUNCTIONS
# ==========================================
def authenticate_user(username, password):
    """ Authenticates a user against the SQLite database """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pwd = _hash_password(password)

        cursor.execute("SELECT role, status FROM users WHERE username = ? AND password = ?", (username, hashed_pwd))
        row = cursor.fetchone()
        conn.close()

        if row:
            role = row["role"]
            status = row["status"]
            if status.lower() in ["approved", "active"]:
                return "SUCCESS", role, "Login Successful"
            else:
                return "FAILED", "user", "Account pending approval by Admin."
        else:
            return "FAILED", "user", "Invalid username or password."
    except Exception as e:
        return "FAILED", "user", f"Database error: {str(e)}"

def register_user(username, password, role="user"):
    """ Registers a new user in the database """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pwd = _hash_password(password)

        cursor.execute("INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)",
                       (username, hashed_pwd, role, "approved"))
        conn.commit()
        conn.close()
        return True, "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Choose another."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

# Alias function names for backward compatibility
authenticate = authenticate_user
login = authenticate_user
login_user = authenticate_user
register = register_user
