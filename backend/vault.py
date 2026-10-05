import os
import hashlib

def _derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', passphrase.encode('utf-8'), salt, 100000, dklen=32)

def encrypt_file(file_path: str, passphrase: str = "CyberShieldSecretKey"):
    if not os.path.exists(file_path):
        return False, "File does not exist."
    try:
        salt = os.urandom(16)
        key = _derive_key(passphrase, salt)
        with open(file_path, 'rb') as f:
            data = f.read()
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(data):
            block_key = hashlib.sha256(key + counter.to_bytes(4, 'big')).digest()
            keystream.extend(block_key)
            counter += 1
        encrypted_data = bytes([d ^ k for d, k in zip(data, keystream[:len(data)])])
        out_path = file_path + ".enc"
        with open(out_path, 'wb') as f:
            f.write(salt + encrypted_data)
        return True, f"File encrypted successfully: {out_path}"
    except Exception as e:
        return False, f"Encryption failed: {str(e)}"

def decrypt_file(file_path: str, passphrase: str = "CyberShieldSecretKey"):
    if not os.path.exists(file_path):
        return False, "Encrypted file does not exist."
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        if len(content) < 16:
            return False, "Invalid encrypted file format."
        salt = content[:16]
        encrypted_data = content[16:]
        key = _derive_key(passphrase, salt)
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(encrypted_data):
            block_key = hashlib.sha256(key + counter.to_bytes(4, 'big')).digest()
            keystream.extend(block_key)
            counter += 1
        decrypted_data = bytes([d ^ k for d, k in zip(encrypted_data, keystream[:len(encrypted_data)])])
        out_path = file_path.replace(".enc", "_decrypted")
        with open(out_path, 'wb') as f:
            f.write(decrypted_data)
        return True, f"File decrypted successfully: {out_path}"
    except Exception as e:
        return False, f"Decryption failed: {str(e)}"

def shred_file(file_path: str, passes: int = 3):
    if not os.path.exists(file_path):
        return False, "File does not exist."
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "ba+", buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
        os.remove(file_path)
        return True, "File securely shredded and deleted."
    except Exception as e:
        return False, f"Shredding failed: {str(e)}"
