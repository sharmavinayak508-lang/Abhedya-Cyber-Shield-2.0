"""Optional link to the CyberShield Portal (no Tkinter here).

Create data/portal.json to switch it on:
    {"server": "http://127.0.0.1:5000", "key": "<DEVICE_KEY>"}
The desktop app then reports system stats plus its own security score
to the portal every few seconds. Without that file nothing happens.
"""
import json
import os
import platform
import socket
import threading
import time
import urllib.request

import psutil

from backend import security_score
from config import PATHS


def _load():
    path = os.path.join(PATHS["data"], "portal.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        cfg = json.load(f)
    return cfg if cfg.get("server") and cfg.get("key") else None


def build_payload():
    procs = []
    for p in psutil.process_iter(["name", "memory_percent"]):
        try:
            procs.append((p.info["name"] or "?", round(p.info["memory_percent"] or 0, 1)))
        except psutil.Error:
            pass
    procs.sort(key=lambda x: -x[1])
    net = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(None), "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent,
        "host": socket.gethostname(), "os": f"{platform.system()} {platform.release()}",
        "uptime": int(time.time() - psutil.boot_time()), "procs": len(psutil.pids()),
        "top": procs[:5], "sent": net.bytes_sent, "recv": net.bytes_recv,
        "battery": None, "desktop_score": security_score.get_score(),
    }


def send(cfg, payload):
    req = urllib.request.Request(cfg["server"].rstrip("/") + "/api/agent/report",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "X-Device-Key": cfg["key"]})
    urllib.request.urlopen(req, timeout=5).read()


def start(interval=3):
    cfg = _load()
    if not cfg:
        return False

    def loop():
        while True:
            try:
                send(cfg, build_payload())
            except Exception:
                pass
            time.sleep(interval)
    threading.Thread(target=loop, daemon=True).start()
    return True
