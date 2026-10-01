"""CPU / RAM numbers for the live chart."""
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False


def get_usage():
    """Returns (cpu_percent, ram_percent) or None when psutil is missing."""
    if not HAS_PSUTIL:
        return None
    return psutil.cpu_percent(interval=None), psutil.virtual_memory().percent
