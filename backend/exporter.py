"""Export logs to CSV."""
import csv
import os
import time

from config import PATHS


def export_logs_csv(rows):
    """rows: list of (id, timestamp, severity, message). Returns the file path."""
    os.makedirs(PATHS["export_dir"], exist_ok=True)
    path = os.path.join(PATHS["export_dir"], f"cybershield_logs_{int(time.time())}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "timestamp", "severity", "message"])
        writer.writerows(rows)
    return path
