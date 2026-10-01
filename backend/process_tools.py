"""Process listing, simple suspicious-process rules and safe termination."""
import os

from backend.logger import log_event

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

SUSPICIOUS_PATH_PARTS = ("/tmp/", "\\temp\\", "/downloads/", "\\downloads\\", "\\appdata\\local\\temp\\")
HIGH_MEMORY_PERCENT = 25.0


def flag_reason(exe, memory_percent):
    """Returns a short reason string, or '' when the process looks normal."""
    lowered = (exe or "").lower()
    if any(part in lowered for part in SUSPICIOUS_PATH_PARTS):
        return "Runs from temp/downloads folder"
    if memory_percent and memory_percent > HIGH_MEMORY_PERCENT:
        return "Very high memory use"
    return ""


def list_processes():
    """Returns list of dicts: pid, name, user, memory, flag."""
    if not HAS_PSUTIL:
        raise RuntimeError("psutil is not installed.")
    rows = []
    for proc in psutil.process_iter(["pid", "name", "username", "exe", "memory_percent"]):
        info = proc.info
        mem = info.get("memory_percent") or 0.0
        rows.append({
            "pid": info["pid"],
            "name": info.get("name") or "?",
            "user": info.get("username") or "SYSTEM",
            "memory": round(mem, 1),
            "flag": flag_reason(info.get("exe"), mem),
        })
    return sorted(rows, key=lambda r: r["memory"], reverse=True)


def terminate(pid):
    """Terminate a process. Returns its name. Refuses to kill this program."""
    if not HAS_PSUTIL:
        raise RuntimeError("psutil is not installed.")
    if pid == os.getpid():
        raise ValueError("Refusing to terminate CyberShield itself.")
    proc = psutil.Process(pid)
    name = proc.name()
    proc.terminate()
    log_event(f"Terminated process {pid} ({name})", "CRITICAL")
    return name
