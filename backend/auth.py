import hashlib
import sqlite3
import os

DB_PATH = os.path.join("data", "cybershield.db") if os.path.exists("data") else "cybershield.db"

def _hash_password(password: str) -> str:
    """ Computes SHA-256 hash of password """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_auth_db():
    """ Ensures users table exists with required fields """
    if not os.path.exists("data") and "data" in DB_PATH:
        os.makedirs("data", exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            company TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Ensure default admin account exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_pwd_hash = _hash_password("admin")
        cursor.execute(
            "INSERT INTO users (username, email, password, company, role, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", "admin@cybershield.com", admin_pwd_hash, "Admin Corp", "admin", "approved")
        )
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """ Authenticates user and checks approval status """
    init_auth_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    pwd_hash = _hash_password(password)
    cursor.execute("SELECT role, status FROM users WHERE username = ? AND password = ?", (username, pwd_hash))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return "FAILED", None, "Invalid username or password."
    
    role, status = user[0], user[1]
    
    if status == "pending":
        return "PENDING", None, "Account is pending Admin approval."
    elif status == "rejected":
        return "REJECTED", None, "Account request was rejected by Admin."
    
    return "SUCCESS", role, "Login successful."

def register_user(username, email, password, company=""):
    """ Registers a new pending user request """
    init_auth_db()
    if not username or not password or not email:
        return False, "Username, email, and password are required."
        
    pwd_hash = _hash_password(password)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, company, role, status) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, pwd_hash, company, "user", "pending")
        )
        conn.commit()
        conn.close()
        return True, "Registration request submitted! Awaiting admin approval."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
