"""Host network information and live connections (real data only)."""
import socket

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False


def get_host_info():
    info = {"hostname": socket.gethostname(), "local_ip": "unknown", "route_ip": "unavailable", "interfaces": []}
    try:
        info["local_ip"] = socket.gethostbyname(info["hostname"])
    except OSError:
        pass
    # A UDP "connect" sends no packets; it only asks the OS which interface would be used.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1.0)
    try:
        s.connect(("8.8.8.8", 80))
        info["route_ip"] = s.getsockname()[0]
    except OSError:
        pass
    finally:
        s.close()
    if HAS_PSUTIL:
        for name, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    info["interfaces"].append((name, a.address))
    return info


def get_connections(limit=40):
    """Returns (connections, error). Each connection: (local_ip, lport, remote_ip, rport, status)."""
    if not HAS_PSUTIL:
        return [], "psutil is not installed."
    try:
        rows = [
            (c.laddr.ip, c.laddr.port, c.raddr.ip, c.raddr.port, c.status)
            for c in psutil.net_connections(kind="inet")
            if c.raddr and c.laddr
        ]
        return rows[:limit], ""
    except (psutil.AccessDenied, PermissionError):
        return [], "Access denied. Run as administrator/root to see all connections."
    except Exception as exc:
        return [], str(exc)
