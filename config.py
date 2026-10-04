import os
from pathlib import Path

# --- BASE ---
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'cybershield.db'}")
SECURE_VAULT_PATH = BASE_DIR / "secure_vault"
SECURE_VAULT_PATH.mkdir(exist_ok=True)

# --- APP ---
APP_NAME = "CyberShield 2.0"
SECRET_KEY = os.getenv("SECRET_KEY", "CYBERSHIELD-2-0-SUPER-SECRET-KEY-CHANGE-IN-PROD-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- THEME for old main.py (Tkinter) ---
THEME = {
    "bg_dark": "#0a0e1a",
    "primary": "#00d4ff",
    "secondary": "#0a0e1a",
    "accent": "#00ff88",
    "danger": "#ff4757",
    "text": "#e0e0e0"
}
THEME_COLORS = THEME

# --- PATHS for old app.py that does `from config import PATHS` ---
PATHS = {
    "BASE_DIR": BASE_DIR,
    "DATABASE_URL": DATABASE_URL,
    "SECURE_VAULT": SECURE_VAULT_PATH,
    "DB_PATH": BASE_DIR / "cybershield.db"
}

