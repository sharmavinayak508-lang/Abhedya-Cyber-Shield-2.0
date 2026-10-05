import sqlite3
import hashlib
import os

DB_PATH = os.path.join("data", "cybershield.db")

def _get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_auth_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            company TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Seed default Admin account if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_hash = _hash_password("admin")
        cursor.execute(
            "INSERT INTO users (username, email, password, company, role, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", "admin@cybershield.com", admin_hash, "CyberShield Corp", "admin", "approved")
        )
    conn.commit()
    conn.close()

# Initialize database
init_auth_db()


def register_user(username, email, password, company="", role="user"):
    """Registers a new user with 'pending' status awaiting admin approval."""
    if not username or not email or not password:
        return False, "Username, Email, and Password are required."

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pwd = _hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, email, password, company, role, status) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, hashed_pwd, company, role, "pending")
        )
        conn.commit()
        conn.close()

        # Send notification to Admin (Console / Log)
        _notify_admin_new_registration(username, email, company)

        return True, "Registration submitted! Please wait for Admin approval before logging in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Choose another."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def authenticate_user(username, password):
    """Authenticates user and enforces approval status check."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pwd = _hash_password(password)

        cursor.execute(
            "SELECT role, status, email FROM users WHERE username = ? AND password = ?",
            (username, hashed_pwd)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            role = row["role"]
            status = row["status"]
            if str(status).lower() == "approved":
                return "SUCCESS", role, "Login Successful"
            elif str(status).lower() == "pending":
                return "FAILED", "user", "Account is PENDING approval by Admin."
            elif str(status).lower() == "rejected":
                return "FAILED", "user", "Account request has been REJECTED by Admin."
            else:
                return "FAILED", "user", f"Account status: {status}"
        else:
            return "FAILED", "user", "Invalid username or password."
    except Exception as e:
        return "FAILED", "user", f"Database error: {str(e)}"


def _notify_admin_new_registration(username, email, company):
    """Simulates sending an email alert to the admin."""
    print(f"\n[EMAIL SENT TO ADMIN] New user registration pending approval:\n - Username: {username}\n - Email: {email}\n - Company: {company or 'N/A'}\n")

# Aliases
authenticate = authenticate_user
login = authenticate_user
register = register_user
