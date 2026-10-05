import hashlib
import json
import urllib.request
import urllib.error

def get_file_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def scan_hash_virustotal(file_hash: str, api_key: str = None):
    if not api_key:
        return {"status": "No API Key Provided", "positives": 0, "total": 0}

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    req = urllib.request.Request(url, headers={"x-apikey": api_key})

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                stats = data['data']['attributes']['last_analysis_stats']
                return {
                    "status": "Malicious" if stats['malicious'] > 0 else "Clean",
                    "positives": stats['malicious'],
                    "total": sum(stats.values())
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"status": "Clean / Unseen in Cloud", "positives": 0, "total": 0}
        return {"status": f"HTTP Error {e.code}", "positives": 0, "total": 0}
    except Exception as e:
        return {"status": f"Connection Error: {str(e)}", "positives": 0, "total": 0}

    return {"status": "API Query Failed", "positives": 0, "total": 0}
