import sqlite3
import os

DB_PATH = os.path.join("data", "cybershield.db")

def _get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_pending_users():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, company, role, created_at FROM users WHERE status = 'pending'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetch_all_users():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, company, role, status, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_user_status(username, status):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()

def fetch_user_stats():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as cnt FROM users GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    
    stats = {"total": 0, "approved": 0, "pending": 0, "rejected": 0}
    for r in rows:
        st = r["status"].lower()
        if st in stats:
            stats[st] = r["cnt"]
        stats["total"] += r["cnt"]
    return stats

def fetch_logs(limit=15):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, level, message FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
