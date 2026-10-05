import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Core Config Imports with Fallback Protection
import config

PATHS = getattr(config, "PATHS", {
    "data": "data",
    "db": "data/cybershield.db",
    "bg_image": "assets/bg.jpg"
})

THEMES = getattr(config, "THEMES", {
    "Dark Cyber": {
        "bg": "#0f172a",
        "card": "#1e293b",
        "accent": "#38bdf8",
        "text": "#f8fafc"
    },
    "Light Modern": {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "accent": "#0284c7",
        "text": "#0f172a"
    },
    "Matrix Green": {
        "bg": "#051105",
        "card": "#0d260d",
        "accent": "#22c55e",
        "text": "#f0fdf4"
    }
})

# Backend Security Modules
from backend import auth, database, logger, scanner, password_gen, honeypot, ai_analyst
from backend import vault, network_monitor, face_auth, threat_intel

class CyberShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invincible Cyber Shield v2.0 - Enterprise Security Suite")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # Database Initialization
        database.init_database()

        # Session State
        self.current_user = None
        self.user_role = "user"
        self.current_theme = "Dark Cyber"

        # Window Layout Frames
        self.sidebar = None
        self.main_content = None

        self.render_login_screen()

    # ==========================================
    # LOGIN & REGISTRATION WORKFLOW
    # ==========================================
    def render_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
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
            
            status, role, msg = auth.authenticate_user(user, pwd)
            if status == "SUCCESS":
                self.current_user = user
                self.user_role = role
                logger.log_event(f"User '{user}' logged in successfully.", "INFO")
                self.render_main_dashboard()
            else:
                messagebox.showerror("Authentication Failed", msg)

        def handle_register():
            user = username_ent.get().strip()
            pwd = password_ent.get().strip()
            
            if not user or not pwd:
                messagebox.showwarning("Input Error", "Please provide both username and password.")
                return

            success, msg = auth.register_user(user, pwd)
            if success:
                messagebox.showinfo("Registration Submitted", msg)
            else:
                messagebox.showerror("Registration Error", msg)

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

        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        self.configure(bg=theme["bg"])

        # Sidebar
        self.sidebar = tk.Frame(self, bg=theme["card"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="CYBER SHIELD", font=("Helvetica", 14, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(20, 5))
        tk.Label(self.sidebar, text=f"Agent: {self.current_user}\nRole: {self.user_role.upper()}", font=("Consolas", 9), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 20))

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

        if self.user_role == "admin":
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
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

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

        # Recent Logs Frame
        tk.Label(self.main_content, text="Recent Audit Logs", font=("Helvetica", 14, "bold"), fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        log_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=12, relief="flat", padx=10, pady=10)
        log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        logs = database.fetch_logs(limit=15)
        for l in logs:
            log_box.insert("end", f"[{l[1]}] [{l[2]}] {l[3]}\n")
        log_box.config(state="disabled")

    # ==========================================
    # PAGE 2: BIOMETRICS & IAM
    # ==========================================
    def render_biometrics_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        tk.Label(self.main_content, text="Biometric & Identity Management", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        tk.Label(card, text="FACIAL BIOMETRIC VERIFICATION", font=("Helvetica", 12, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w")
        tk.Label(card, text="Verifies live camera stream against human face detection model.", fg="#94a3b8", bg=theme["card"]).pack(anchor="w", pady=(0, 15))

        def trigger_camera_auth():
            messagebox.showinfo("Biometric Auth", "Opening webcam... Please look directly at the camera.")
            match = face_auth.verify_face_biometric()
            if match:
                messagebox.showinfo("Access Granted", "Biometric verification successful! Facial match confirmed.")
                logger.log_event(f"Biometric face verification PASSED for {self.current_user}", "INFO")
            else:
                messagebox.showerror("Access Denied", "Face verification failed or webcam timed out.")
                logger.log_event(f"Biometric face verification FAILED for {self.current_user}", "WARN")

        tk.Button(card, text="Start Face ID Scan", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=8, command=trigger_camera_auth).pack(anchor="w")

    # ==========================================
    # PAGE 3: AES SECURE VAULT & SHREDDER
    # ==========================================
    def render_vault_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        tk.Label(self.main_content, text="AES-256 Vault & DoD File Shredder", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        # Encrypt File Box
        enc_card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=15)
        enc_card.pack(fill="x", padx=20, pady=10)

        tk.Label(enc_card, text="SECURE FILE ENCRYPTION", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")
        
        secret_ent = tk.Entry(enc_card, show="*", font=("Helvetica", 10), width=30)
        secret_ent.pack(anchor="w", pady=5)
        secret_ent.insert(0, "MasterSecretKey")

        def select_and_encrypt():
            filepath = filedialog.askopenfilename(title="Select Document/Photo to Encrypt")
            secret = secret_ent.get().strip()
            if filepath and secret:
                if vault.encrypt_file(filepath, secret):
                    messagebox.showinfo("Vault Success", f"Encrypted and stored in vault: {os.path.basename(filepath)}.enc")
                    logger.log_event(f"Encrypted file '{os.path.basename(filepath)}'", "INFO")
                else:
                    messagebox.showerror("Vault Error", "Failed to encrypt file.")

        tk.Button(enc_card, text="Select & Encrypt File", bg="#3b82f6", fg="white", font=("Helvetica", 10, "bold"), relief="flat", command=select_and_encrypt).pack(anchor="w", pady=5)

        # Shredder Box
        shred_card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=15)
        shred_card.pack(fill="x", padx=20, pady=10)

        tk.Label(shred_card, text="DoD 5220.22-M 3-PASS FILE SHREDDER", font=("Helvetica", 12, "bold"), fg="#ef4444", bg=theme["card"]).pack(anchor="w")
        tk.Label(shred_card, text="Overwrites file with Zeros, Ones, and Cryptographic Random Bytes before deletion.", fg="#94a3b8", bg=theme["card"]).pack(anchor="w", pady=(0, 10))

        def select_and_shred():
            filepath = filedialog.askopenfilename(title="SELECT FILE TO PERMANENTLY DESTROY")
            if filepath:
                confirm = messagebox.askyesno("WARNING", f"Are you sure you want to permanently shred:\n{filepath}?")
                if confirm:
                    if vault.dod_shred_file(filepath):
                        messagebox.showinfo("Shred Complete", "File permanently destroyed via DoD 3-pass wipe.")
                        logger.log_event(f"Shredded file '{os.path.basename(filepath)}'", "WARN")
                    else:
                        messagebox.showerror("Shred Error", "Could not shred file.")

        tk.Button(shred_card, text="Select File & Permanently Shred", bg="#ef4444", fg="white", font=("Helvetica", 10, "bold"), relief="flat", command=select_and_shred).pack(anchor="w")

    # ==========================================
    # PAGE 4: NETWORK TELEMETRY
    # ==========================================
    def render_network_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        tk.Label(self.main_content, text="Active Network & Socket Telemetry", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        # Wi-Fi Profiles Section
        wifi_profiles = network_monitor.audit_saved_wifi_profiles()
        wifi_card = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=10)
        wifi_card.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(wifi_card, text=f"Saved Device Wi-Fi Profiles Found: {len(wifi_profiles)}", font=("Helvetica", 10, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w")
        tk.Label(wifi_card, text=", ".join(wifi_profiles[:5]), font=("Consolas", 9), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

        # Active Network Connections Table
        net_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 9), height=15, relief="flat", padx=10, pady=10)
        net_box.pack(fill="both", expand=True, padx=20, pady=10)

        conns = network_monitor.get_active_network_connections()
        net_box.insert("end", f"{'PID':<8} | {'PROCESS':<20} | {'LOCAL ADDRESS':<22} | {'REMOTE ADDRESS':<22}\n")
        net_box.insert("end", "-" * 80 + "\n")

        for c in conns:
            net_box.insert("end", f"{c['pid']:<8} | {c['process'][:18]:<20} | {c['local']:<22} | {c['remote']:<22}\n")

        net_box.config(state="disabled")

    # ==========================================
    # PAGE 5: THREAT INTEL SCANNER
    # ==========================================
    def render_threat_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        tk.Label(self.main_content, text="Cloud Threat Intelligence (VirusTotal)", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        tk.Label(card, text="FILE SHA-256 REPUTATION LOOKUP", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")
        
        res_lbl = tk.Label(card, text="Select a file to calculate its SHA-256 hash and verify against cloud threat feeds.", fg="#94a3b8", bg=theme["card"])
        res_lbl.pack(anchor="w", pady=(5, 15))

        def run_threat_scan():
            filepath = filedialog.askopenfilename()
            if filepath:
                sha256_hash = threat_intel.get_file_sha256(filepath)
                vt_result = threat_intel.scan_hash_virustotal(sha256_hash, api_key=None)
                
                res_text = f"File: {os.path.basename(filepath)}\nSHA-256: {sha256_hash}\nCloud Status: {vt_result['status']}"
                res_lbl.config(text=res_text, fg=theme["accent"])
                logger.log_event(f"Scanned hash '{sha256_hash[:10]}...' - Status: {vt_result['status']}", "INFO")

        tk.Button(card, text="Select File & Query Threat Feed", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=8, command=run_threat_scan).pack(anchor="w")

    # ==========================================
    # UTILITY PAGES (SCANNER, PASS, AI, ADMIN)
    # ==========================================
    def render_scanner_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Local Endpoint Integrity Scanner", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)
        
        scan_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        scan_box.pack(fill="both", expand=True, padx=20, pady=10)

        def start_scan():
            scan_box.delete("1.0", "end")
            scan_box.insert("end", "Initiating System File Integrity Audit...\n\n")
            results = scanner.run_full_system_scan()
            for r in results:
                scan_box.insert("end", f"[{r['type']}] File: {r['file']} | Status: {r['status']}\n")

        tk.Button(self.main_content, text="Run Integrity Audit", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), command=start_scan).pack(padx=20, anchor="w")

    def render_password_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Cryptographic Password Utilities", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        card.pack(fill="x", padx=20, pady=10)

        pass_lbl = tk.Label(card, text="Generated Password: ---", font=("Consolas", 12, "bold"), fg=theme["accent"], bg=theme["card"])
        pass_lbl.pack(anchor="w", pady=(0, 10))

        def gen_pass():
            p = password_gen.generate_high_entropy_password(16)
            pass_lbl.config(text=f"Generated Password: {p}")

        tk.Button(card, text="Generate 16-Char Pass", bg="#3b82f6", fg="white", command=gen_pass).pack(anchor="w")

    def render_ai_page(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="AI Security Analyst Insights", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        ai_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        ai_box.pack(fill="both", expand=True, padx=20, pady=10)

        insights = ai_analyst.generate_security_assessment()
        ai_box.insert("end", insights)
        ai_box.config(state="disabled")

    def render_admin_panel(self):
        self.clear_content()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Admin User Management & Audit Panel", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        # Metrics Card
        stats = database.fetch_user_stats()
        stats_frame = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(stats_frame, text="USER REGISTRATION METRICS", font=("Helvetica", 11, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w", pady=(0, 5))
        metrics_text = f"Total Registered: {stats['total']}  |  Approved: {stats['approved']}  |  Pending: {stats['pending']}  |  Rejected: {stats['rejected']}"
        tk.Label(stats_frame, text=metrics_text, font=("Consolas", 11, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

        # Pending Requests
        tk.Label(self.main_content, text="Pending Access Requests", font=("Helvetica", 14, "bold"), fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=(10, 5))
        pending_users = database.fetch_pending_users()

        if not pending_users:
            tk.Label(self.main_content, text="No pending registration requests.", fg="#94a3b8", bg=theme["bg"]).pack(anchor="w", padx=20, pady=(0, 10))
        else:
            for u in pending_users:
                row = tk.Frame(self.main_content, bg=theme["card"], padx=10, pady=10)
                row.pack(fill="x", padx=20, pady=5)

                tk.Label(row, text=f"Agent: {u['username']}  |  Role: {u['role']}", fg=theme["text"], bg=theme["card"], font=("Helvetica", 11)).pack(side="left")

                def approve(username=u['username']):
                    database.set_user_status(username, "approved")
                    logger.log_event(f"Admin approved account for '{username}'.", "INFO")
                    messagebox.showinfo("Success", f"Approved user {username}")
                    self.render_admin_panel()

                def reject(username=u['username']):
                    database.set_user_status(username, "rejected")
                    logger.log_event(f"Admin rejected account for '{username}'.", "WARN")
                    messagebox.showinfo("Rejected", f"Rejected user {username}")
                    self.render_admin_panel()

                tk.Button(row, text="Approve", bg="#10b981", fg="white", command=approve).pack(side="right", padx=5)
                tk.Button(row, text="Reject", bg="#ef4444", fg="white", command=reject).pack(side="right")

if __name__ == "__main__":
    app = CyberShieldApp()
    app.mainloop()
