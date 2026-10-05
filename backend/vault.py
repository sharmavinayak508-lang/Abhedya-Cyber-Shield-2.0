import os
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_DIR = os.path.join("data", "vault")
os.makedirs(VAULT_DIR, exist_ok=True)

def derive_key(user_secret: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(user_secret.encode()))

def encrypt_file(file_path: str, user_secret: str) -> bool:
    if not os.path.exists(file_path):
        return False
    
    salt = secrets.token_bytes(16)
    key = derive_key(user_secret, salt)
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)
    filename = os.path.basename(file_path) + ".enc"
    out_path = os.path.join(VAULT_DIR, filename)

    with open(out_path, "wb") as f:
        f.write(salt + encrypted_data)
        
    return True

def decrypt_file(enc_filename: str, user_secret: str, out_dir: str) -> bool:
    enc_path = os.path.join(VAULT_DIR, enc_filename)
    if not os.path.exists(enc_path):
        return False

    with open(enc_path, "rb") as f:
        file_bytes = f.read()

    salt = file_bytes[:16]
    encrypted_data = file_bytes[16:]

    try:
        key = derive_key(user_secret, salt)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        orig_filename = enc_filename.rsplit(".enc", 1)[0]
        out_path = os.path.join(out_dir, orig_filename)

        with open(out_path, "wb") as f:
            f.write(decrypted_data)
        return True
    except Exception:
        return False

def dod_shred_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    length = os.path.getsize(file_path)
    with open(file_path, "ba+", buffering=0) as f:
        f.seek(0)
        f.write(b"\x00" * length)
        f.flush()

        f.seek(0)
        f.write(b"\xFF" * length)
        f.flush()

        f.seek(0)
        f.write(secrets.token_bytes(length))
        f.flush()

    os.remove(file_path)
    return True
