# CyberShield

A desktop **Security Operations Center (SOC) dashboard** written in Python (Tkinter).
It combines file-integrity monitoring, an encrypted quarantine vault, a honeytoken trap,
live system telemetry and password tools in one dark, terminal-style interface.

> Educational project. It demonstrates security concepts; it is not a replacement for a real antivirus/EDR.

## Features

| Area | What it does |
|---|---|
| **Security score** | Live 0-100 gauge. Warnings/critical events lower it, quiet time restores it. |
| **Live charts** | CPU/RAM line chart and events-by-severity bar chart. |
| **File hash auditor** | SHA-256 of any file, checked against a signature list (EICAR test file + demo file). |
| **Folder integrity monitor** | Take a baseline of hashes, later report modified / new / deleted files. |
| **Encrypted vault** | Master-password vault (PBKDF2 + Fernet/AES). Threats are encrypted, verified, then securely shredded. Restore any time. |
| **Honeytoken** | Decoy credentials file; any modification raises a CRITICAL alert. |
| **PE analyzer** | Static parse of .exe/.dll headers, sections, entropy (packing hint) and imports. Never runs the file. |
| **Process auditor** | Process list with suspicious-path / high-memory flags and confirmed termination. |
| **Network monitor** | Host info and a live map of real remote connections. |
| **Password toolkit** | Strength checker, secure generator, change-login-password. |
| **Logs** | SQLite history with severity filter, search and CSV export. |
| **Login** | Salted PBKDF2 hashes and a 30-second lock-out after 3 failures. |

## Project structure

```
cybershield/
├── main.py              # entry point
├── config.py            # theme + file locations
├── backend/             # all logic, no Tkinter code
│   ├── database.py  logger.py  security_score.py  auth.py
│   ├── crypto.py  file_tools.py  integrity.py  honeytoken.py
│   ├── process_tools.py  network_tools.py  pe_analyzer.py
│   └── password_tools.py  rsa_demo.py  system_stats.py  exporter.py
├── frontend/            # all screens, no business logic
│   ├── login.py  dashboard.py  widgets.py  base_page.py
│   └── overview_page.py  files_page.py  process_page.py  network_page.py
│       vault_page.py  password_page.py  logs_page.py
└── tests/test_backend.py
```

Rule: **backend never imports Tkinter; frontend only calls backend functions.**

## Install and run

Requires Python 3.8+ with Tkinter (included on Windows/macOS installers;
on Debian/Ubuntu run `sudo apt install python3-tk`).

```bash
git clone <your-repo-url>
cd cybershield
python -m venv .venv
# Windows:  .venv\Scripts\activate        macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Default login on first run: `admin` / `Admin@123` (change it on the **PASSWORDS** page).

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Demo script (2 minutes)

1. Sign in, show the **Overview** gauge and live charts.
2. **Vault & Traps** → create a vault with a master password.
3. Create a text file containing exactly `CYBERSHIELD-TEST-FILE`.
   **File Security** → scan it → confirm quarantine. The file is encrypted into the vault and the original is shredded.
4. **Vault & Traps** → deploy the honeytoken → *Simulate tampering* → watch the CRITICAL alert and the score drop.
5. **File Security** → choose a folder → *Create baseline* → edit a file in it → *Scan for changes*.
6. **Logs** → filter by CRITICAL → export CSV.

## Limitations (honest notes)

- Signature detection uses a tiny hash list; it demonstrates the idea only.
- Secure shredding is best-effort on SSDs and journaling file systems.
- The RSA panel uses small primes for teaching and is **not** secure.
- Seeing every network connection / process may need administrator or root rights.
- Single-user login stored locally in SQLite.

## Possible future work

Anomaly detection (Isolation Forest), VirusTotal hash lookup, email/Telegram alerts, plugin system.

## License

MIT, see `LICENSE`.
