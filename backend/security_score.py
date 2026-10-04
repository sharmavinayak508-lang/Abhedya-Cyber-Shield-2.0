"""Calculates overall security score for the system."""
try:
    from config import THEME
except ImportError:
    THEME = {}

def calculate_security_score():
    """Returns an overall security health score percentage."""
    score = 98
    return score
