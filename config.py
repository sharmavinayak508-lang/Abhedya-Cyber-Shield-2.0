"""Central configuration: theme colours, fonts and file locations.

Every runtime file (database, vault, exports, honeytoken) lives in ./data
so the project folder stays clean and .gitignore can exclude it.
"""
import os

APP_NAME = "CyberShield"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

THEME = {
    "bg_dark": "#020204",
    "bg_panel": "#07080e",
    "bg_terminal": "#040509",
    "accent_cyan": "#00f0ff",
    "accent_lime": "#39ff14",
    "accent_magenta": "#ff0055",
    "accent_purple": "#7b2cbf",
    "accent_orange": "#ffa500",
    "text_main": "#e0e6ed",
    "text_muted": "#505a69",
    "font_family": "Consolas",
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
