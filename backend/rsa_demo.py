"""Tiny RSA for teaching only (small primes = NOT secure)."""
import math
import random


def _is_prime(n):
    if n < 2:
        return False
    return all(n % i for i in range(2, math.isqrt(n) + 1))


def generate_keys():
    """Returns dict with p, q, n, phi, e, d."""
    primes = [x for x in range(100, 250) if _is_prime(x)]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])
    n, phi = p * q, (p - 1) * (q - 1)
    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    d = pow(e, -1, phi)
    return {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d}


def encrypt_text(text, e, n):
    return [pow(ord(c), e, n) for c in text]


def decrypt_text(numbers, d, n):
    return "".join(chr(pow(c, d, n)) for c in numbers)
