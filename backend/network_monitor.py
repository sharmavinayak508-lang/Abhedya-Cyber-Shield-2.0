import socket
import subprocess
import psutil

def get_active_network_connections():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED' and conn.raddr:
            try:
                proc = psutil.Process(conn.pid)
                pname = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pname = "System Process"

            connections.append({
                "pid": conn.pid,
                "process": pname,
                "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                "status": conn.status
            })
    return connections[:15]

def audit_saved_wifi_profiles():
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "profiles"], encoding="utf-8", errors="ignore")
        profiles = [line.split(":")[1].strip() for line in output.split("\n") if "All User Profile" in line]
        return profiles
    except Exception:
        return ["Wi-Fi profile audit unavailable"]

def check_open_port(ip: str, port: int, timeout=0.5) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    result = s.connect_ex((ip, port))
    s.close()
    return result == 0
