"""Thread-safe event queue. Any thread may log; the UI drains it."""
import datetime
import queue

from backend import database, security_score

telemetry_queue = queue.Queue()


def log_event(msg, severity="INFO"):
    telemetry_queue.put(
        {"msg": msg, "severity": severity, "timestamp": datetime.datetime.now()}
    )
    security_score.register(severity)


def drain_queue():
    """Return all pending events and persist them to SQLite."""
    items = []
    while True:
        try:
            items.append(telemetry_queue.get_nowait())
        except queue.Empty:
            break
    if items:
        try:
            database.insert_logs(
                [(i["timestamp"].isoformat(timespec="seconds"), i["severity"], i["msg"]) for i in items]
            )
        except Exception:
            pass
    return items


def format_item(item):
    stamp = item["timestamp"].strftime("[%H:%M:%S]")
    return f"{stamp} [{item['severity']}] {item['msg']}"
