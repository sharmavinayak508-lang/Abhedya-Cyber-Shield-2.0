"""Master-password vault (Fernet/AES) with a key derived via PBKDF2.

The key is never stored. Only a random salt and a small encrypted "check"
token are saved, so a correct password can be recognised after restart.
"""
import base64
import os

from config import PATHS

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False

KDF_ITERATIONS = 390_000
CHECK_PLAINTEXT = b"CYBERSHIELD-VAULT-OK"
_fernet = None


def _derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=KDF_ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def vault_exists():
    return os.path.exists(PATHS["vault_salt"]) and os.path.exists(PATHS["vault_check"])


def is_unlocked():
    return _fernet is not None


def lock_vault():
    global _fernet
    _fernet = None


def setup_vault(password):
    """Create a new vault. Raises ValueError for weak passwords."""
    global _fernet
    if not HAS_CRYPTO:
        raise RuntimeError("The 'cryptography' package is not installed.")
    if len(password) < 8:
        raise ValueError("Master password must be at least 8 characters.")
    os.makedirs(PATHS["vault_dir"], exist_ok=True)
    salt = os.urandom(16)
    fernet = Fernet(_derive_key(password, salt))
    with open(PATHS["vault_salt"], "wb") as f:
        f.write(salt)
    with open(PATHS["vault_check"], "wb") as f:
        f.write(fernet.encrypt(CHECK_PLAINTEXT))
    _fernet = fernet


def unlock_vault(password):
    """Returns True when the password is correct."""
    global _fernet
    if not HAS_CRYPTO or not vault_exists():
        return False
    with open(PATHS["vault_salt"], "rb") as f:
        salt = f.read()
    with open(PATHS["vault_check"], "rb") as f:
        check = f.read()
    fernet = Fernet(_derive_key(password, salt))
    try:
        ok = fernet.decrypt(check) == CHECK_PLAINTEXT
    except InvalidToken:
        return False
    if ok:
        _fernet = fernet
    return ok


def encrypt_bytes(data):
    if _fernet is None:
        raise PermissionError("Vault is locked.")
    return _fernet.encrypt(data)


def decrypt_bytes(token):
    if _fernet is None:
        raise PermissionError("Vault is locked.")
    return _fernet.decrypt(token)
