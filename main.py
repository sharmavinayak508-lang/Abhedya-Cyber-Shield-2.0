import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- CONFIG FALLBACKS ---
try:
    import config
    PATHS = getattr(config, "PATHS", {"data": "data", "db": "data/cybershield.db", "bg_image": "assets/bg.jpg"})
    THEMES = getattr(config, "THEMES", {
        "Dark Cyber": {"bg": "#0f172a", "card": "#1e293b", "accent": "#38bdf8", "text": "#f8fafc"},
        "Light Modern": {"bg": "#f8fafc", "card": "#ffffff", "accent": "#0284c7", "text": "#0f172a"},
        "Matrix Green": {"bg": "#051105", "card": "#0d260d", "accent": "#22c55e", "text": "#f0fdf4"}
    })
except Exception:
    PATHS = {"data": "data", "db": "data/cybershield.db", "bg_image": "assets/bg.jpg"}
    THEMES = {
        "Dark Cyber": {"bg": "#0f172a", "card": "#1e293b", "accent": "#38bdf8", "text": "#f8fafc"}
    }

# --- DIRECT BACKEND IMPORTS (BYPASSING __init__.py) ---
try:
    from backend import auth
except ImportError:
    auth = None

try:
    from backend import database
except ImportError:
    database = None

try:
    from backend import logger
except ImportError:
    logger = None

try:
    from backend import scanner
except ImportError:
    scanner = None

try:
    from backend import password_gen
except ImportError:
    password_gen = None

try:
    from backend import honeypot
except ImportError:
    honeypot = None

try:
    from backend import ai_analyst
except ImportError:
    ai_analyst = None

try:
    from backend import vault
except ImportError:
    vault = None

try:
    from backend import network_monitor
except ImportError:
    network_monitor = None

try:
    from backend import face_auth
except ImportError:
    face_auth = None

try:
    from backend import threat_intel
except ImportError:
    threat_intel = None


class CyberShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invincible Cyber Shield v2.0 - Enterprise Security Suite")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # Database Initialization
        if database and hasattr(database, "init_database"):
            database.init_database()

        # Session State
        self.current_user = None
        self.user_role = "user"
        self.current_theme = "Dark Cyber"

        # Window Layout Frames
        self.sidebar = None
        self.main_content = None

        self.render_login_screen()

    def log_safe(self, message, level="INFO"):
        if logger and hasattr(logger, "log_event"):
            logger.log_event(message, level)

    # ==========================================
    # LOGIN & REGISTRATION WORKFLOW
    # ==========================================
    def render_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        self.configure(bg=theme["bg"])

        login_frame = tk.Frame(self, bg=theme["card"], padx=30, pady=30, highlightthickness=1, highlightbackground=theme["accent"])
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="INVINCIBLE CYBER SHIELD", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(0, 5))
        tk.Label(login_frame, text="Enterprise Endpoint Security & Access Control", font=("Helvetica", 10), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 20))

        tk.Label(login_frame, text="Username", fg=theme["text"], bg=theme["card"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        username_ent = tk.Entry(login_frame, font=("Helvetica", 11), bg=theme["bg"], fg=theme["text"], insertbackground=theme["text"])
        username_ent.pack(fill="x", pady=(0, 15))

        tk.Label(login_frame, text="Password", fg=theme["text"], bg=theme["card"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        password_ent = tk.Entry(login_frame, show="*", font=("Helvetica", 11), bg=theme["bg"], fg=theme["text"], insertbackground=theme["text"])
        password_ent.pack(fill="x", pady=(0, 20))

        def handle_login():
            user = username_ent.get().strip()
            pwd = password_ent.get().strip()

            if not auth:
                messagebox.showerror("Error", "Auth module missing.")
                return

            # Dynamic function matching for backend.auth
            auth_func = None
            for func_name in ["authenticate_user", "login", "login_user", "authenticate", "verify_user", "check_login"]:
                if hasattr(auth, func_name):
                    auth_func = getattr(auth, func_name)
                    break

            if not auth_func:
                messagebox.showerror("Auth Error", "No suitable login function found in backend/auth.py")
                return

            try:
                res = auth_func(user, pwd)
                status, role, msg = "FAILED", "user", "Invalid credentials"

                if isinstance(res, tuple):
                    if len(res) == 3:
                        status, role, msg = res
                    elif len(res) == 2:
                        status, msg = res
                elif isinstance(res, bool):
                    status = "SUCCESS" if res else "FAILED"
                    msg = "Login Successful" if res else "Invalid credentials"

                if str(status).upper() in ["SUCCESS", "TRUE", "OK"]:
                    self.current_user = user
                    self.user_role = role
                    self.log_safe(f"User '{user}' logged in successfully.", "INFO")
                    self.render_main_dashboard()
                else:
                    messagebox.showerror("Authentication Failed", str(msg))
            except Exception as e:
                messagebox.showerror("Login Error", f"Authentication error: {str(e)}")

        def handle_register():
            user = username_ent.get().strip()
            pwd = password_ent.get().strip()

            if not user or not pwd:
                messagebox.showwarning("Input Error", "Please provide both username and password.")
                return

            if not auth:
                messagebox.showerror("Error", "Auth module missing.")
                return

            reg_func = None
            for func_name in ["register_user", "register", "create_user", "add_user"]:
                if hasattr(auth, func_name):
                    reg_func = getattr(auth, func_name)
                    break

            if not reg_func:
                messagebox.showerror("Auth Error", "No suitable registration function found in backend/auth.py")
                return

            try:
                res = reg_func(user, pwd)
                if isinstance(res, tuple):
                    success, msg = res[0], res[1]
                else:
                    success, msg = bool(res), "Registration completed."

                if success:
                    messagebox.showinfo("Registration Submitted", str(msg))
                else:
                    messagebox.showerror("Registration Error", str(msg))
            except Exception as e:
                messagebox.showerror("Registration Exception", f"Error: {str(e)}")

        btn_frame = tk.Frame(login_frame, bg=theme["card"])
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Login", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=5, command=handle_login).pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Button(btn_frame, text="Register", bg="#334155", fg="white", font=("Helvetica", 10), relief="flat", padx=15, pady=5, command=handle_register).pack(side="right", expand=True, fill="x", padx=(5, 0))

    # ==========================================
    # MAIN DASHBOARD & NAVIGATION
    # ==========================================
    def render_main_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        self.configure(bg=theme["bg"])

        # Sidebar
        self.sidebar = tk.Frame(self, bg=theme["card"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="CYBER SHIELD", font=("Helvetica", 14, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(20, 5))
        tk.Label(self.sidebar, text=f"Agent: {self.current_user}\nRole: {str(self.user_role).upper()}", font=("Consolas", 9), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 20))

        # Main Workspace Panel
        self.main_content = tk.Frame(self, bg=theme["bg"])
        self.main_content.pack(side="right", expand=True, fill="both")

        # Dynamic Nav Links
        nav_options = [
            ("Dashboard", self.render_overview_page),
            ("Biometrics & IAM", self.render_biometrics_page),
            ("AES Secure Vault", self.render_vault_page),
            ("Network Telemetry", self.render_network_page),
            ("Threat Intel Scan", self.render_threat_page),
            ("System Scanner", self.render_scanner_page),
            ("Password Tools", self.render_password_page),
            ("AI Analyst", self.render_ai_page)
        ]

        if str(self.user_role).lower() == "admin":
            nav_options.append(("Admin Panel", self.render_admin_panel))

        for text, command in nav_options:
            btn = tk.Button(self.sidebar, text=f"  {text}", anchor="w", font=("Helvetica", 10, "bold"), fg=theme["text"], bg=theme["card"], activebackground=theme["accent"], activeforeground="black", relief="flat", pady=8, command=command)
            btn.pack(fill="x", padx=10, pady=2)

        # Logout Session
        logout_btn = tk.Button(self.sidebar, text="  Logout Session", anchor="w", font=("Helvetica", 10), fg="#ef4444", bg=theme["card"], relief="flat", pady=8, command=self.render_login_screen)
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=15)

        self.render_overview_page()

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # ==========================================
    # PAGE 1: OVERVIEW DASHBOARD
    # ==========================================
    def render_overview_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])

        tk.Label(self.main_content, text="System Operations Overview", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        stats_frame = tk.Frame(self.main_content, bg=theme["bg"])
        stats_frame.pack(fill="x", padx=20, pady=10)

        cards = [
            ("ENDPOINT STATUS", "PROTECTED / ACTIVE", "#10b981"),
            ("CRYPTO VAULT", "AES-256 ENCRYPTED", theme["accent"]),
            ("NETWORK GUARD", "REAL-TIME MONITORING", "#3b82f6")
        ]

        for title, val, color in cards:
            c_frame = tk.Frame(stats_frame, bg=theme["card"], padx=15, pady=15, highlightthickness=1, highlightbackground=color)
            c_frame.pack(side="left", expand=True, fill="both", padx=5)
            tk.Label(c_frame, text=title, font=("Helvetica", 9, "bold"), fg="#94a3b8", bg=theme["card"]).pack(anchor="w")
            tk.Label(c_frame, text=val, font=("Consolas", 12, "bold"), fg=color, bg=theme["card"]).pack(anchor="w", pady=(5, 0))

        tk.Label(self.main_content, text="Recent Audit Logs", font=("Helvetica", 14, "bold"), fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=(20, 5))

        log_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=12, relief="flat", padx=10, pady=10)
        log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if database and hasattr(database, "fetch_logs"):
            logs = database.fetch_logs(limit=15)
            for l in logs:
                log_box.insert("end", f"[{l[1]}] [{l[2]}] {l[3]}\n")
        else:
            log_box.insert("end", "Database logging initialized.\n")
        log_box.config(state="disabled")

    # ==========================================
    # PAGE 2: BIOMETRICS & IAM
    # ==========================================
    def render_biometrics_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])

        tk.Label(self.main_content, text="Biometric & Identity Management", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        tk.Label(card, text="FACIAL BIOMETRIC VERIFICATION", font=("Helvetica", 12, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w")
        tk.Label(card, text="Verifies live camera stream against human face detection model.", fg="#94a3b8", bg=theme["card"]).pack(anchor="w", pady=(0, 15))

        def trigger_camera_auth():
            if not face_auth:
                messagebox.showerror("Module Error", "Face Auth module is missing.")
                return
            messagebox.showinfo("Biometric Auth", "Opening webcam... Please look directly at the camera.")
            func = getattr(face_auth, "verify_face_biometric", getattr(face_auth, "verify_face", None))
            if func:
                match = func()
                if match:
                    messagebox.showinfo("Access Granted", "Biometric verification successful!")
                    self.log_safe(f"Biometric face verification PASSED for {self.current_user}", "INFO")
                else:
                    messagebox.showerror("Access Denied", "Face verification failed.")
            else:
                messagebox.showerror("Module Error", "Biometric method unavailable.")

        tk.Button(card, text="Start Face ID Scan", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=8, command=trigger_camera_auth).pack(anchor="w")

    # ==========================================
    # PAGE 3: AES SECURE VAULT & SHREDDER
    # ==========================================
    def render_vault_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])

        tk.Label(self.main_content, text="AES-256 Vault & DoD File Shredder", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        enc_card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=15)
        enc_card.pack(fill="x", padx=20, pady=10)

        tk.Label(enc_card, text="SECURE FILE ENCRYPTION", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

        secret_ent = tk.Entry(enc_card, show="*", font=("Helvetica", 10), width=30)
        secret_ent.pack(anchor="w", pady=5)
        secret_ent.insert(0, "MasterSecretKey")

        def select_and_encrypt():
            if not vault:
                messagebox.showerror("Module Error", "Vault module missing.")
                return
            filepath = filedialog.askopenfilename(title="Select File to Encrypt")
            secret = secret_ent.get().strip()
            if filepath and secret:
                func = getattr(vault, "encrypt_file", getattr(vault, "encrypt", None))
                if func and func(filepath, secret):
                    messagebox.showinfo("Vault Success", f"Encrypted file: {os.path.basename(filepath)}")
                    self.log_safe(f"Encrypted file '{os.path.basename(filepath)}'", "INFO")
                else:
                    messagebox.showerror("Vault Error", "Failed to encrypt file.")

        tk.Button(enc_card, text="Select & Encrypt File", bg="#3b82f6", fg="white", font=("Helvetica", 10, "bold"), relief="flat", command=select_and_encrypt).pack(anchor="w", pady=5)

        shred_card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=15)
        shred_card.pack(fill="x", padx=20, pady=10)

        tk.Label(shred_card, text="DoD 5220.22-M 3-PASS FILE SHREDDER", font=("Helvetica", 12, "bold"), fg="#ef4444", bg=theme["card"]).pack(anchor="w")

        def select_and_shred():
            if not vault:
                messagebox.showerror("Module Error", "Vault module missing.")
                return
            filepath = filedialog.askopenfilename(title="SELECT FILE TO SHRED")
            if filepath:
                confirm = messagebox.askyesno("WARNING", f"Are you sure you want to shred:\n{filepath}?")
                if confirm:
                    func = getattr(vault, "dod_shred_file", getattr(vault, "shred_file", None))
                    if func and func(filepath):
                        messagebox.showinfo("Shred Complete", "File permanently destroyed.")
                        self.log_safe(f"Shredded file '{os.path.basename(filepath)}'", "WARN")
                    else:
                        messagebox.showerror("Shred Error", "Could not shred file.")

        tk.Button(shred_card, text="Select File & Permanently Shred", bg="#ef4444", fg="white", font=("Helvetica", 10, "bold"), relief="flat", command=select_and_shred).pack(anchor="w")

    # ==========================================
    # PAGE 4: NETWORK TELEMETRY
    # ==========================================
    def render_network_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])

        tk.Label(self.main_content, text="Active Network & Socket Telemetry", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        if network_monitor:
            net_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 9), height=15, relief="flat", padx=10, pady=10)
            net_box.pack(fill="both", expand=True, padx=20, pady=10)

            func = getattr(network_monitor, "get_active_network_connections", getattr(network_monitor, "get_connections", None))
            conns = func() if func else []
            
            net_box.insert("end", f"{'PID':<8} | {'PROCESS':<20} | {'LOCAL ADDRESS':<22} | {'REMOTE ADDRESS':<22}\n")
            net_box.insert("end", "-" * 80 + "\n")

            for c in conns:
                if isinstance(c, dict):
                    net_box.insert("end", f"{c.get('pid',''):<8} | {str(c.get('process',''))[:18]:<20} | {c.get('local',''):<22} | {c.get('remote',''):<22}\n")
                else:
                    net_box.insert("end", f"{str(c)}\n")

            net_box.config(state="disabled")
        else:
            tk.Label(self.main_content, text="Network monitor module not available.", fg="#ef4444", bg=theme["bg"]).pack(padx=20, pady=20)

    # ==========================================
    # PAGE 5: THREAT INTEL SCANNER
    # ==========================================
    def render_threat_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])

        tk.Label(self.main_content, text="Cloud Threat Intelligence (VirusTotal)", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        tk.Label(card, text="FILE SHA-256 REPUTATION LOOKUP", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

        res_lbl = tk.Label(card, text="Select a file to calculate its hash and query threat feeds.", fg="#94a3b8", bg=theme["card"])
        res_lbl.pack(anchor="w", pady=(5, 15))

        def run_threat_scan():
            if not threat_intel:
                messagebox.showerror("Error", "Threat intel module not loaded.")
                return
            filepath = filedialog.askopenfilename()
            if filepath:
                hash_func = getattr(threat_intel, "get_file_sha256", getattr(threat_intel, "get_hash", None))
                sha256_hash = hash_func(filepath) if hash_func else "N/A"
                res_lbl.config(text=f"File: {os.path.basename(filepath)}\nSHA-256: {sha256_hash}", fg=theme["accent"])

        tk.Button(card, text="Select File & Query Threat Feed", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=8, command=run_threat_scan).pack(anchor="w")

    # ==========================================
    # UTILITY PAGES (SCANNER, PASS, AI, ADMIN)
    # ==========================================
    def render_scanner_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        tk.Label(self.main_content, text="Local Endpoint Integrity Scanner", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        scan_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        scan_box.pack(fill="both", expand=True, padx=20, pady=10)

        def start_scan():
            scan_box.delete("1.0", "end")
            if not scanner:
                scan_box.insert("end", "Scanner module not available.\n")
                return
            scan_box.insert("end", "Initiating System File Integrity Audit...\n\n")
            func = getattr(scanner, "run_full_system_scan", getattr(scanner, "scan", None))
            results = func() if func else []
            for r in results:
                scan_box.insert("end", f"{str(r)}\n")

        tk.Button(self.main_content, text="Run Integrity Audit", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), command=start_scan).pack(padx=20, anchor="w")

    def render_password_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        tk.Label(self.main_content, text="Cryptographic Password Utilities", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        pass_lbl = tk.Label(card, text="Generated Password: ---", font=("Consolas", 12, "bold"), fg=theme["accent"], bg=theme["card"])
        pass_lbl.pack(anchor="w", pady=(0, 10))

        def gen_pass():
            func = getattr(password_gen, "generate_high_entropy_password", getattr(password_gen, "generate_password", None)) if password_gen else None
            p = func(16) if func else "PasswordModuleUnavailable"
            pass_lbl.config(text=f"Generated Password: {p}")

        tk.Button(card, text="Generate 16-Char Pass", bg="#3b82f6", fg="white", command=gen_pass).pack(anchor="w")

    def render_ai_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        tk.Label(self.main_content, text="AI Security Analyst Insights", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        ai_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        ai_box.pack(fill="both", expand=True, padx=20, pady=10)

        func = getattr(ai_analyst, "generate_security_assessment", getattr(ai_analyst, "get_assessment", None)) if ai_analyst else None
        if func:
            insights = func()
            ai_box.insert("end", str(insights))
        else:
            ai_box.insert("end", "AI Analyst module not loaded.")
        ai_box.config(state="disabled")

    def render_admin_panel(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, list(THEMES.values())[0])
        tk.Label(self.main_content, text="Admin User Management & Audit Panel", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        stats_func = getattr(database, "fetch_user_stats", None) if database else None
        stats = stats_func() if stats_func else {"total": 0, "approved": 0, "pending": 0, "rejected": 0}
        
        stats_frame = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(stats_frame, text="USER REGISTRATION METRICS", font=("Helvetica", 11, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w", pady=(0, 5))
        metrics_text = f"Total Registered: {stats.get('total',0)}  |  Approved: {stats.get('approved',0)}  |  Pending: {stats.get('pending',0)}"
        tk.Label(stats_frame, text=metrics_text, font=("Consolas", 11, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")


if __name__ == "__main__":
    app = CyberShieldApp()
    app.mainloop()
