# backend/__init__.py

# Ensure all backend submodules are accessible when imported from backend
from . import auth
from . import database
from . import logger
from . import password_gen
from . import honeypot
from . import ai_analyst

# Optional modules with dynamic import fallback
try:
    from . import scanner
except ImportError:
    scanner = None

try:
    from . import vault
except ImportError:
    vault = None

try:
    from . import network_monitor
except ImportError:
    network_monitor = None

try:
    from . import face_auth
except ImportError:
    face_auth = None

try:
    from . import threat_intel
except ImportError:
    threat_intel = None
