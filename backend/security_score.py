"""Live security score (0-100). Events lower it, quiet time slowly restores it."""
import threading

from config import THEME

_lock = threading.Lock()
_score = 100
PENALTY = {"CRITICAL": 15, "ERROR": 5, "WARN": 3}


def register(severity):
    global _score
    with _lock:
        _score = max(0, _score - PENALTY.get(severity, 0))
        return _score


def recover(points=1):
    global _score
    with _lock:
        _score = min(100, _score + points)
        return _score


def get_score():
    with _lock:
        return _score


def reset():
    global _score
    with _lock:
        _score = 100


def get_label(score=None):
    """Returns (text, colour) for a score."""
    score = get_score() if score is None else score
    if score >= 80:
        return "SECURE", THEME["accent_lime"]
    if score >= 50:
        return "ELEVATED RISK", THEME["accent_orange"]
    return "CRITICAL", THEME["accent_magenta"]
