import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'cybershield.db'}")
APP_NAME = "CyberShield 2.0"
THEME = {"bg_dark": "#0a0e1a", "primary": "#00d4ff", "secondary": "#0a0e1a", "accent": "#00ff88", "danger": "#ff4757", "text": "#e0e0e0"}
THEME_COLORS = THEME
SECRET_KEY = "CHANGE-THIS-TO-A-LONG-RANDOM-STRING"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
