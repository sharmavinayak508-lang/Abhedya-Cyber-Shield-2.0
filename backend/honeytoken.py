"""Honeytoken (canary file): a decoy that should never change. Any edit raises an alert."""
import hashlib
import json
import os
import threading

from backend.logger import log_event
from config import PATHS

# AWS's documented example credentials: fake by design.
DECOY = {"aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
         "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}


def _hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class HoneytokenSentinel:
    def __init__(self, interval=1.0):
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    @property
    def active(self):
        return self._thread is not None and self._thread.is_alive()

    def deploy(self):
        """Write the decoy file and start watching it. Returns its path."""
        path = PATHS["honeytoken"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(DECOY, f)
        log_event(f"Honeytoken deployed: {os.path.basename(path)}", "WARN")
        self.stop()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._watch, args=(path, _hash(path), self._stop), daemon=True)
        self._thread.start()
        return path

    def _watch(self, path, baseline, stop):
        while not stop.wait(self.interval):
            if not os.path.exists(path):
                log_event(f"TRAP TRIPPED: decoy {os.path.basename(path)} was DELETED!", "CRITICAL")
                return
            try:
                current = _hash(path)
            except OSError:
                continue
            if current != baseline:
                log_event(f"TRAP TRIPPED: decoy {os.path.basename(path)} was MODIFIED!", "CRITICAL")
                baseline = current

    def simulate_tamper(self):
        """Demo helper: modify the decoy so the trap fires."""
        with open(PATHS["honeytoken"], "a") as f:
            f.write("\n# tampered")

    def stop(self):
        self._stop.set()


sentinel = HoneytokenSentinel()
