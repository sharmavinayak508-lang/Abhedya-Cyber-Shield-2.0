import os
import sqlite3
from config import PATHS

DB_PATH = PATHS["db"]

def get_connection():
    os.makedirs(PATHS["data"], exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            theme TEXT DEFAULT 'Dark Cyber'
        )
    """)

    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()

def fetch_pending_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE status = 'pending'")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": r[0], "role": r[1]} for r in rows]

def set_user_status(username, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()

def update_user_theme(username, theme):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET theme = ? WHERE username = ?", (theme, username))
    conn.commit()
    conn.close()

def fetch_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, level, message FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
