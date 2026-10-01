"""Password strength analysis and secure password generation."""
import math
import secrets
import string

COMMON = {
    "password", "123456", "12345678", "qwerty", "admin", "admin123", "letmein",
    "welcome", "iloveyou", "abc123", "password1", "111111", "123456789",
}
SYMBOLS = "!@#$%^&*()_+-=[]{};:,.<>?/"


def analyze_password(pwd):
    """Returns dict: score (0-6), level, label, feedback list, entropy_bits."""
    if not pwd:
        return {"score": 0, "level": "empty", "label": "NO INPUT", "feedback": [], "entropy_bits": 0.0}

    feedback = []
    score = 0
    has_lower = any(c in string.ascii_lowercase for c in pwd)
    has_upper = any(c in string.ascii_uppercase for c in pwd)
    has_digit = any(c in string.digits for c in pwd)
    has_symbol = any(c in string.punctuation for c in pwd)

    if len(pwd) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters.")
    if len(pwd) >= 14:
        score += 1
    else:
        feedback.append("14+ characters is much safer.")
    for ok, msg in ((has_lower, "Add lowercase letters."), (has_upper, "Add uppercase letters."),
                    (has_digit, "Add digits."), (has_symbol, "Add symbols (!@#$...).")):
        if ok:
            score += 1
        else:
            feedback.append(msg)

    pool = 26 * has_lower + 26 * has_upper + 10 * has_digit + 32 * has_symbol
    entropy = round(len(pwd) * math.log2(pool), 1) if pool else 0.0

    if pwd.lower() in COMMON:
        score = 0
        feedback.insert(0, "This is one of the most common passwords.")

    if score <= 2:
        level, label = "critical", "VERY WEAK"
    elif score <= 4:
        level, label = "weak", "WEAK"
    elif score == 5:
        level, label = "good", "GOOD"
    else:
        level, label = "strong", "STRONG"
    return {"score": score, "level": level, "label": label, "feedback": feedback, "entropy_bits": entropy}


def generate_password(length=16):
    """Cryptographically secure password containing every character class."""
    length = max(12, min(64, int(length)))
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits, SYMBOLS]
    chars = [secrets.choice(p) for p in pools]
    allchars = "".join(pools)
    chars += [secrets.choice(allchars) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
