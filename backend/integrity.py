"""Folder integrity monitor: take a baseline of hashes, later report changes."""
import os

from backend import database
from backend.file_tools import sha256_file
from backend.logger import log_event

MAX_FILES = 5000
MAX_SIZE = 100 * 1024 * 1024  # skip files over 100 MB


def _snapshot(folder):
    """Returns {relative_path: (sha256, size)} for every readable file."""
    result = {}
    for root, _dirs, files in os.walk(folder, followlinks=False):
        for name in files:
            full = os.path.join(root, name)
            try:
                if os.path.islink(full) or os.path.getsize(full) > MAX_SIZE:
                    continue
                rel = os.path.relpath(full, folder)
                result[rel] = (sha256_file(full), os.path.getsize(full))
            except OSError:
                continue
            if len(result) >= MAX_FILES:
                return result
    return result


def _key(folder):
    return os.path.abspath(folder)


def create_baseline(folder):
    """Hash every file now and store it as the trusted state. Returns file count."""
    if not os.path.isdir(folder):
        raise ValueError("Folder does not exist.")
    snap = _snapshot(folder)
    database.save_baseline(_key(folder), [(rel, sha, size) for rel, (sha, size) in snap.items()])
    log_event(f"Integrity baseline created for {folder} ({len(snap)} files)", "INFO")
    return len(snap)


def scan(folder):
    """Compare the folder with its baseline.

    Returns dict with lists: modified, new, deleted and an unchanged count.
    """
    if not os.path.isdir(folder):
        raise ValueError("Folder does not exist.")
    baseline = database.load_baseline(_key(folder))
    if not baseline:
        raise ValueError("No baseline for this folder yet. Create one first.")
    current = {rel: sha for rel, (sha, _s) in _snapshot(folder).items()}

    modified = sorted(r for r in current if r in baseline and current[r] != baseline[r])
    new = sorted(r for r in current if r not in baseline)
    deleted = sorted(r for r in baseline if r not in current)
    unchanged = len(current) - len(modified) - len(new)

    if modified or deleted:
        log_event(f"INTEGRITY ALERT in {folder}: {len(modified)} modified, {len(deleted)} deleted, {len(new)} new", "CRITICAL")
    elif new:
        log_event(f"Integrity scan of {folder}: {len(new)} new file(s)", "WARN")
    else:
        log_event(f"Integrity scan of {folder}: all {unchanged} files unchanged", "INFO")
    return {"modified": modified, "new": new, "deleted": deleted, "unchanged": unchanged}
