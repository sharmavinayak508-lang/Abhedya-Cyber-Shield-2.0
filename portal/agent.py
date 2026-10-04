"""CyberShield agent: runs on the customer's PC and reports status to the portal.
Usage: python agent.py --server http://127.0.0.1:5000 --key <DEVICE_KEY>"""
import argparse, json, os, platform, socket, time, urllib.request
import psutil

psutil.cpu_percent(None)

def collect():
    procs = []
    for p in psutil.process_iter(["name", "memory_percent"]):
        try:
            procs.append((p.info["name"] or "?", round(p.info["memory_percent"] or 0, 1)))
        except psutil.Error:
            pass
    procs.sort(key=lambda x: -x[1])
    net = psutil.net_io_counters()
    bat = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    return {
        "cpu": psutil.cpu_percent(None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent,
        "host": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "uptime": int(time.time() - psutil.boot_time()),
        "procs": len(psutil.pids()),
        "top": procs[:5],
        "sent": net.bytes_sent, "recv": net.bytes_recv,
        "battery": None if bat is None else round(bat.percent),
    }

def post(server, key, data):
    req = urllib.request.Request(server.rstrip("/") + "/api/agent/report",
        data=json.dumps(data).encode(), method="POST",
        headers={"Content-Type": "application/json", "X-Device-Key": key})
    urllib.request.urlopen(req, timeout=5).read()

def run(server, key, interval=3):
    while True:
        try:
            post(server, key, collect())
        except Exception as e:
            print("agent: could not report:", e)
        time.sleep(interval)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:5000")
    ap.add_argument("--key", required=True)
    ap.add_argument("--interval", type=int, default=3)
    a = ap.parse_args()
    print("CyberShield agent reporting to", a.server, "- Ctrl+C to stop")
    run(a.server, a.key, a.interval)
