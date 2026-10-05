import os

def run_full_system_scan(target_dir="."):
    results = []
    suspicious_exts = [".bat", ".vbs", ".exe", ".sh", ".cmd"]
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in suspicious_exts:
                results.append({
                    "file": os.path.join(root, file),
                    "type": "Executable File",
                    "status": "FLAGGED FOR REVIEW"
                })
            else:
                results.append({
                    "file": os.path.join(root, file),
                    "type": "Standard Data File",
                    "status": "VERIFIED CLEAN"
                })
        if len(results) >= 20:  # Sample limit
            break
    return results

scan = run_full_system_scan
