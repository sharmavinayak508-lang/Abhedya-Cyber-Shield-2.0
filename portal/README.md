# CyberShield Portal
Customer login checked against a database, then a live status page for the customer's computer.

## Run (Windows/Mac/Linux)
    pip install -r requirements.txt
    python app.py run
Open http://127.0.0.1:5000 and sign in with **demo@cybershield.in / Demo@123**.
A demo agent starts automatically so live data appears at once.

## Manage customers (you, the owner)
    python app.py add-user a@b.com "Asha" "Strong#Pass1" --verify
    python app.py verify a@b.com          # approve a self-registered account
    python app.py list
    python app.py add-device a@b.com "Asha laptop"   # prints the agent key
## Customer's computer
    python agent.py --server http://YOUR_SERVER:5000 --key <DEVICE_KEY>

## How it works
Browser -> /api/login -> SQLite users table (PBKDF2 hash) -> session cookie -> /api/status.
Agent -> /api/agent/report (device key, stored hashed) -> telemetry table.
Unverified or wrong credentials show "Not verified". 5 failed logins lock that email+IP for 60s.
Before real deployment: serve over HTTPS and run behind gunicorn/waitress.
