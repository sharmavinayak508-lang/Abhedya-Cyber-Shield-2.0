"""Central configuration: theme colours, fonts and file locations.

Every runtime file (database, vault, exports, honeytoken) lives in ./data
so the project folder stays clean and .gitignore can exclude it.
"""
import os

APP_NAME = "CyberShield"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

THEME = {
    "bg_dark": "#0b1624",
    "bg_panel": "#122238",
    "bg_terminal": "#0a121d",
    "accent_cyan": "#3dc2b8",
    "accent_lime": "#4cd07d",
    "accent_magenta": "#ff7b6e",
    "accent_purple": "#7d8fb3",
    "accent_orange": "#e0a84a",
    "text_main": "#e6edf5",
    "text_muted": "#8fa0b5",
    "font_family": "Segoe UI",
}

# A plain dict on purpose: backend modules read it at call time,
# so unit tests can point it at a temporary folder.
PATHS = {
    "data": DATA_DIR,
    "vault_dir": os.path.join(DATA_DIR, "secure_vault"),
    "export_dir": os.path.join(DATA_DIR, "exports"),
    "db": os.path.join(DATA_DIR, "system_telemetry.db"),
    "honeytoken": os.path.join(DATA_DIR, "canary_aws_config.json"),
    "vault_salt": os.path.join(DATA_DIR, "vault.salt"),
    "vault_check": os.path.join(DATA_DIR, "vault.check"),
}
