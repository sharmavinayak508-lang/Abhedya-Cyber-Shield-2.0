import sqlite3
import os

DB_PATH = os.path.join("data", "cybershield.db")

def log_event(message, level="INFO"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (level, message) VALUES (?, ?)", (level, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[LOG ERROR] {e}")
