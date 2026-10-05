import secrets
import string

def generate_high_entropy_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(secrets.choice(alphabet) for _ in range(length))

generate_password = generate_high_entropy_password
