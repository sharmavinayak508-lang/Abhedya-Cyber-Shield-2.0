"""CyberShield Portal: customer login (checked against a database) + live computer status."""
import argparse, hashlib, json, os, secrets, sqlite3, threading, time
from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "portal.db")
KEYFILE = os.path.join(BASE, "secret.key")
DEMO_KEYFILE = os.path.join(BASE, "demo_agent.key")
ONLINE_SECS = 15
MAX_FAILS, LOCK_SECS = 5, 60

if not os.path.exists(KEYFILE):
    with open(KEYFILE, "w") as f:
        f.write(secrets.token_hex(32))
app = Flask(__name__, static_folder="static")
app.config.update(SECRET_KEY=open(KEYFILE).read(), SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=8 * 3600)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT,
  pw_hash TEXT NOT NULL, verified INTEGER NOT NULL DEFAULT 0, created REAL);
CREATE TABLE IF NOT EXISTS devices(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT,
  key_hash TEXT UNIQUE NOT NULL, last_seen REAL);
CREATE TABLE IF NOT EXISTS telemetry(id INTEGER PRIMARY KEY, device_id INTEGER NOT NULL, ts REAL,
  cpu REAL, ram REAL, disk REAL, snap TEXT);
CREATE INDEX IF NOT EXISTS t_dev ON telemetry(device_id, id);
"""
DUMMY = generate_password_hash("not-a-real-password")
FAILS = {}

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d:
        d.close()

@app.after_request
def headers(r):
    r.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                      "Referrer-Policy": "no-referrer", "Cache-Control": "no-store"})
    return r

def hkey(k):
    return hashlib.sha256(k.encode()).hexdigest()

def err(msg, code, **kw):
    return jsonify(error=msg, message=kw.pop("message", msg), **kw), code

def body():
    return request.get_json(silent=True) or {}

def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    u = db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return u if u and u["verified"] else None

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/login")
def login():
    d = body()
    email, pw = str(d.get("email", "")).strip().lower(), str(d.get("password", ""))
    k = (email, request.remote_addr)
    n, until = FAILS.get(k, (0, 0))
    if until > time.time():
        return err("locked", 429, message=f"Too many attempts. Try again in {int(until - time.time())} seconds.")
    u = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    ok = check_password_hash(u["pw_hash"] if u else DUMMY, pw) and u is not None
    if not ok:
        n += 1
        FAILS[k] = (0, time.time() + LOCK_SECS) if n >= MAX_FAILS else (n, 0)
        return err("not_verified", 401, message="Not verified")
    FAILS.pop(k, None)
    if not u["verified"]:
        return err("pending", 403, message="Not verified")
    session.clear()
    session.permanent = True
    session["uid"] = u["id"]
    return jsonify(ok=True, name=u["name"])

@app.post("/api/register")
def register():
    d = body()
    email, name, pw = str(d.get("email", "")).strip().lower(), str(d.get("name", "")).strip()[:60], str(d.get("password", ""))
    if "@" not in email or len(email) > 120 or not name:
        return err("invalid", 400, message="Enter your name and a valid email address.")
    if len(pw) < 8:
        return err("weak", 400, message="Password must be at least 8 characters.")
    try:
        db().execute("INSERT INTO users(email,name,pw_hash,verified,created) VALUES(?,?,?,0,?)",
                     (email, name, generate_password_hash(pw), time.time()))
        db().commit()
    except sqlite3.IntegrityError:
        return err("exists", 409, message="That email is already registered.")
    return jsonify(ok=True), 201

@app.get("/api/me")
def me():
    u = current_user()
    return (jsonify(name=u["name"], email=u["email"]) if u else err("auth", 401))

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

def health(s, online):
    if not online:
        return 0
    pen = sum(max(0, v - t) * w for v, t, w in ((s["cpu"], 80, 1.5), (s["ram"], 80, 1.5), (s["disk"], 85, 2)))
    return max(0, round(100 - pen))

@app.get("/api/status")
def status():
    u = current_user()
    if not u:
        return err("auth", 401)
    out = []
    for dv in db().execute("SELECT * FROM devices WHERE user_id=?", (u["id"],)).fetchall():
        rows = db().execute("SELECT ts,cpu,ram,snap FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT 60",
                            (dv["id"],)).fetchall()[::-1]
        age = time.time() - (dv["last_seen"] or 0)
        online = bool(rows) and age < ONLINE_SECS
        snap = json.loads(rows[-1]["snap"]) if rows else None
        out.append(dict(id=dv["id"], name=dv["name"], online=online, age=int(age) if rows else None,
                        snap=snap, score=health(snap, online) if snap else 0,
                        history=[[r["cpu"], r["ram"]] for r in rows]))
    return jsonify(name=u["name"], devices=out)

@app.post("/api/agent/report")
def report():
    key = request.headers.get("X-Device-Key", "")
    dv = db().execute("SELECT * FROM devices WHERE key_hash=?", (hkey(key),)).fetchone() if key else None
    if not dv:
        return err("bad_key", 401)
    s = body()
    try:
        cpu, ram, disk = (float(s[k]) for k in ("cpu", "ram", "disk"))
    except (KeyError, TypeError, ValueError):
        return err("invalid", 400)
    now = time.time()
    c = db()
    c.execute("INSERT INTO telemetry(device_id,ts,cpu,ram,disk,snap) VALUES(?,?,?,?,?,?)",
              (dv["id"], now, cpu, ram, disk, json.dumps(s)[:4000]))
    c.execute("UPDATE devices SET last_seen=? WHERE id=?", (now, dv["id"]))
    c.execute("DELETE FROM telemetry WHERE device_id=? AND id < (SELECT MAX(id)-500 FROM telemetry WHERE device_id=?)",
              (dv["id"], dv["id"]))
    c.commit()
    return jsonify(ok=True)

# ---------- owner CLI ----------
def add_user(email, name, pw, verified):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO users(email,name,pw_hash,verified,created) VALUES(?,?,?,?,?)",
                  (email.lower(), name, generate_password_hash(pw), int(verified), time.time()))

def add_device(email, name):
    key = secrets.token_urlsafe(24)
    with sqlite3.connect(DB) as c:
        r = c.execute("SELECT id FROM users WHERE email=?", (email.lower(),)).fetchone()
        if not r:
            raise SystemExit("No such user")
        c.execute("INSERT INTO devices(user_id,name,key_hash) VALUES(?,?,?)", (r[0], name, hkey(key)))
    return key

def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("--port", type=int, default=5000); r.add_argument("--no-demo-agent", action="store_true")
    u = sp.add_parser("add-user"); u.add_argument("email"); u.add_argument("name"); u.add_argument("password"); u.add_argument("--verify", action="store_true")
    v = sp.add_parser("verify"); v.add_argument("email")
    dv = sp.add_parser("add-device"); dv.add_argument("email"); dv.add_argument("name")
    sp.add_parser("list")
    a = ap.parse_args()
    init_db()
    if a.cmd == "add-user":
        add_user(a.email, a.name, a.password, a.verify); print("User added.")
    elif a.cmd == "verify":
        with sqlite3.connect(DB) as c:
            n = c.execute("UPDATE users SET verified=1 WHERE email=?", (a.email.lower(),)).rowcount
        print("Verified." if n else "No such user.")
    elif a.cmd == "add-device":
        print("Device key (shown once):", add_device(a.email, a.name))
    elif a.cmd == "list":
        with sqlite3.connect(DB) as c:
            for row in c.execute("SELECT email,name,verified FROM users"):
                print(("verified    " if row[2] else "NOT verified"), row[0], "-", row[1])
    else:
        with sqlite3.connect(DB) as c:
            empty = c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        if empty:
            add_user("demo@cybershield.in", "Demo Customer", "Demo@123", True)
            with open(DEMO_KEYFILE, "w") as f:
                f.write(add_device("demo@cybershield.in", "This laptop"))
            print("Created demo account: demo@cybershield.in / Demo@123")
        if not a.no_demo_agent and os.path.exists(DEMO_KEYFILE):
            import agent
            key = open(DEMO_KEYFILE).read().strip()
            threading.Thread(target=lambda: (time.sleep(1.5), agent.run(f"http://127.0.0.1:{a.port}", key, 2)), daemon=True).start()
        print(f"Open http://127.0.0.1:{a.port}")
        app.run(host="127.0.0.1", port=a.port, threaded=True)

if __name__ == "__main__":
    main()
