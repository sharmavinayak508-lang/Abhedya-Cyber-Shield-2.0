"""Application paths and configuration parameters."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

PATHS = {
    "base": BASE_DIR,
    "data": DATA_DIR,
    "db": os.path.join(DATA_DIR, "cybershield.db"),
    "vault_dir": os.path.join(DATA_DIR, "vault"),
    "vault_salt": os.path.join(DATA_DIR, "vault", "vault.salt"),
    "vault_check": os.path.join(DATA_DIR, "vault", "vault.check"),
    "export_dir": os.path.join(DATA_DIR, "exports"),
    "honeytoken": os.path.join(DATA_DIR, "decoy_aws_credentials.json"),
}

THEME = {
    "bg": "#0f172a",
    "sidebar": "#1e293b",
    "card": "#334155",
    "text": "#f8fafc",
    "accent": "#0ea5e9",
    "button": "#0284c7"
}
