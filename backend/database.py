"""SQLite storage: logs, file hashes, folder baselines and user accounts."""
import os
import sqlite3
from contextlib import contextmanager

from config import PATHS


@contextmanager
def _db():
    conn = sqlite3.connect(PATHS["db"])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_database():
    """Create folders and tables (safe to call on every start)."""
    for key in ("data", "vault_dir", "export_dir"):
        os.makedirs(PATHS[key], exist_ok=True)
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, severity TEXT, message TEXT
            );
            CREATE TABLE IF NOT EXISTS file_integrity (
                file_path TEXT PRIMARY KEY, sha256_hash TEXT, last_checked TEXT
            );
            CREATE TABLE IF NOT EXISTS baseline (
                folder TEXT, rel_path TEXT, sha256 TEXT, size INTEGER,
                PRIMARY KEY (folder, rel_path)
            );
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, salt TEXT, pw_hash TEXT, iterations INTEGER
            );
            """
        )


# ---------- logs ----------
def insert_logs(rows):
    """rows: list of (iso_timestamp, severity, message)."""
    with _db() as conn:
        conn.executemany(
            "INSERT INTO security_logs (timestamp, severity, message) VALUES (?, ?, ?)", rows
        )


def fetch_logs(severity=None, search="", limit=500):
    query = "SELECT id, timestamp, severity, message FROM security_logs WHERE 1=1"
    params = []
    if severity and severity != "ALL":
        query += " AND severity = ?"
        params.append(severity)
    if search:
        query += " AND message LIKE ?"
        params.append(f"%{search}%")
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with _db() as conn:
        return [tuple(r) for r in conn.execute(query, params).fetchall()]


# ---------- single-file hashes ----------
def save_hash(path, sha256, when):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO file_integrity VALUES (?, ?, ?)", (path, sha256, when)
        )


# ---------- folder baselines ----------
def save_baseline(folder, entries):
    """entries: list of (rel_path, sha256, size). Replaces any older baseline."""
    with _db() as conn:
        conn.execute("DELETE FROM baseline WHERE folder = ?", (folder,))
        conn.executemany(
            "INSERT INTO baseline (folder, rel_path, sha256, size) VALUES (?, ?, ?, ?)",
            [(folder, *e) for e in entries],
        )


def load_baseline(folder):
    with _db() as conn:
        rows = conn.execute(
            "SELECT rel_path, sha256 FROM baseline WHERE folder = ?", (folder,)
        ).fetchall()
    return {r["rel_path"]: r["sha256"] for r in rows}


# ---------- users ----------
def get_user(username):
    with _db() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return dict(row) if row else None


def add_user(username, salt_hex, hash_hex, iterations):
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
            (username, salt_hex, hash_hex, iterations),
        )
