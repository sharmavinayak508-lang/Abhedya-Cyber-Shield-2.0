import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Dynamic Backend Imports
from backend import auth, database, logger, scanner, password_gen, ai_analyst, vault, network_monitor, face_auth, threat_intel

THEMES = {
    "Dark Cyber": {"bg": "#0f172a", "card": "#1e293b", "accent": "#38bdf8", "text": "#f8fafc"}
}

class CyberShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invincible Cyber Shield v2.0 - Enterprise Security Suite")
        self.geometry("1100(700")
        self.geometry("1100x700")
        self.minsize(950, 600)

        if hasattr(database, "init_database"):
            database.init_database()

        self.current_user = None
        self.user_role = "user"
        self.current_theme = "Dark Cyber"

        self.render_login_screen()

    def log_safe(self, message, level="INFO"):
        if hasattr(logger, "log_event"):
            logger.log_event(message, level)

    # ==========================================
    # LOGIN & REGISTRATION
    # ==========================================
    def render_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = THEMES[self.current_theme]
        self.configure(bg=theme["bg"])

        login_frame = tk.Frame(self, bg=theme["card"], padx=30, pady=30, highlightthickness=1, highlightbackground=theme["accent"])
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="INVINCIBLE CYBER SHIELD", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(0, 5))
        tk.Label(login_frame, text="Enterprise Access & Security Control", font=("Helvetica", 10), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 20))

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
                self.log_safe(f"User '{user}' logged in successfully.", "INFO")
                self.render_main_dashboard()
            else:
                messagebox.showerror("Authentication Failed", msg)

        btn_frame = tk.Frame(login_frame, bg=theme["card"])
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Login", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", padx=15, pady=5, command=handle_login).pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Button(btn_frame, text="Register Request", bg="#334155", fg="white", font=("Helvetica", 10), relief="flat", padx=15, pady=5, command=self.render_registration_modal).pack(side="right", expand=True, fill="x", padx=(5, 0))

    def render_registration_modal(self):
        theme = THEMES[self.current_theme]
        modal = tk.Toplevel(self)
        modal.title("Request Access - User Registration")
        modal.geometry("400x480")
        modal.configure(bg=theme["card"])
        modal.grab_set()

        tk.Label(modal, text="ACCOUNT REGISTRATION", font=("Helvetica", 14, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(15, 5))
        tk.Label(modal, text="Requests require Admin review and authorization.", font=("Helvetica", 9), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 15))

        # Form Fields
        fields = [("Username *", "user"), ("Email Address *", "email"), ("Password *", "pass"), ("Company Name (Optional)", "comp")]
        entries = {}

        for label_text, key in fields:
            tk.Label(modal, text=label_text, fg=theme["text"], bg=theme["card"], font=("Helvetica", 9, "bold")).pack(anchor="w", padx=25)
            ent = tk.Entry(modal, show="*" if key == "pass" else "", font=("Helvetica", 10), bg=theme["bg"], fg=theme["text"], insertbackground=theme["text"])
            ent.pack(fill="x", padx=25, pady=(2, 10))
            entries[key] = ent

        def submit_registration():
            u = entries["user"].get().strip()
            e = entries["email"].get().strip()
            p = entries["pass"].get().strip()
            c = entries["comp"].get().strip()

            success, msg = auth.register_user(u, e, p, c)
            if success:
                messagebox.showinfo("Registration Submitted", msg, parent=modal)
                modal.destroy()
            else:
                messagebox.showerror("Registration Failed", msg, parent=modal)

        tk.Button(modal, text="Submit Request", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), relief="flat", command=submit_registration).pack(fill="x", padx=25, pady=15)

    # ==========================================
    # MAIN DASHBOARD
    # ==========================================
    def render_main_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        theme = THEMES[self.current_theme]
        self.configure(bg=theme["bg"])

        # Sidebar
        self.sidebar = tk.Frame(self, bg=theme["card"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="CYBER SHIELD", font=("Helvetica", 14, "bold"), fg=theme["accent"], bg=theme["card"]).pack(pady=(20, 5))
        tk.Label(self.sidebar, text=f"Agent: {self.current_user}\nRole: {str(self.user_role).upper()}", font=("Consolas", 9), fg="#94a3b8", bg=theme["card"]).pack(pady=(0, 20))

        self.main_content = tk.Frame(self, bg=theme["bg"])
        self.main_content.pack(side="right", expand=True, fill="both")

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
            nav_options.append(("Admin Approval Panel", self.render_admin_panel))

        for text, command in nav_options:
            btn = tk.Button(self.sidebar, text=f"  {text}", anchor="w", font=("Helvetica", 10, "bold"), fg=theme["text"], bg=theme["card"], activebackground=theme["accent"], activeforeground="black", relief="flat", pady=8, command=command)
            btn.pack(fill="x", padx=10, pady=2)

        logout_btn = tk.Button(self.sidebar, text="  Logout Session", anchor="w", font=("Helvetica", 10), fg="#ef4444", bg=theme["card"], relief="flat", pady=8, command=self.render_login_screen)
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=15)

        self.render_overview_page()

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # ==========================================
    # PAGES
    # ==========================================
    def render_overview_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="System Operations Overview", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        log_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        log_box.pack(fill="both", expand=True, padx=20, pady=10)

        logs = database.fetch_logs(limit=15)
        for l in logs:
            log_box.insert("end", f"[{l[1]}] [{l[2]}] {l[3]}\n")
        log_box.config(state="disabled")

    def render_biometrics_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="Biometric & Identity Management", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        def trigger_camera_auth():
            messagebox.showinfo("Biometric Auth", "Opening webcam... Look directly at camera.")
            if face_auth.verify_face_biometric():
                messagebox.showinfo("Access Granted", "Biometric face verification PASSED!")
                self.log_safe(f"Biometric verification PASSED for {self.current_user}", "INFO")
            else:
                messagebox.showerror("Access Denied", "Face verification failed or camera timed out.")

        tk.Button(self.main_content, text="Start Face ID Scan", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), padx=15, pady=8, command=trigger_camera_auth).pack(anchor="w", padx=20, pady=10)

    def render_vault_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="AES-256 Vault & DoD File Shredder", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

    def render_network_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="Active Network Telemetry", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

    def render_threat_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="Threat Intelligence Scanner", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        lbl = tk.Label(self.main_content, text="Select file to analyze SHA-256 hash against threat feeds.", fg=theme["text"], bg=theme["bg"])
        lbl.pack(anchor="w", padx=20, pady=5)

        def run_scan():
            fp = filedialog.askopenfilename()
            if fp:
                h = threat_intel.get_file_sha256(fp)
                res = threat_intel.scan_hash_virustotal(h)
                lbl.config(text=f"File: {os.path.basename(fp)}\nSHA-256: {h}\nStatus: {res['status']}")

        tk.Button(self.main_content, text="Select File & Scan", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), command=run_scan).pack(anchor="w", padx=20, pady=10)

    def render_scanner_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="System Integrity Scanner", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        scan_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        scan_box.pack(fill="both", expand=True, padx=20, pady=10)

        def start_scan():
            scan_box.delete("1.0", "end")
            res = scanner.run_full_system_scan()
            for r in res:
                scan_box.insert("end", f"[{r['type']}] {r['file']} -> {r['status']}\n")

        tk.Button(self.main_content, text="Run Integrity Scan", bg=theme["accent"], fg="black", font=("Helvetica", 10, "bold"), command=start_scan).pack(anchor="w", padx=20)

    def render_password_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="Password Generator", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        pass_lbl = tk.Label(self.main_content, text="Generated Password: ---", font=("Consolas", 12, "bold"), fg=theme["accent"], bg=theme["bg"])
        pass_lbl.pack(anchor="w", padx=20, pady=10)

        def gen():
            p = password_gen.generate_high_entropy_password(16)
            pass_lbl.config(text=f"Generated Password: {p}")

        tk.Button(self.main_content, text="Generate 16-Char Pass", bg="#3b82f6", fg="white", font=("Helvetica", 10, "bold"), command=gen).pack(anchor="w", padx=20)

    def render_ai_page(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="AI Security Assessment", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        ai_box = tk.Text(self.main_content, bg=theme["card"], fg=theme["text"], font=("Consolas", 10), height=15, relief="flat", padx=10, pady=10)
        ai_box.pack(fill="both", expand=True, padx=20, pady=10)

        ai_box.insert("end", ai_analyst.generate_security_assessment())
        ai_box.config(state="disabled")

    def render_admin_panel(self):
        self.clear_content()
        theme = THEMES[self.current_theme]
        tk.Label(self.main_content, text="Admin User Approval Panel", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        pending_users = database.fetch_pending_users()

        if not pending_users:
            tk.Label(self.main_content, text="No pending registration requests.", fg="#94a3b8", bg=theme["bg"]).pack(anchor="w", padx=20, pady=10)
        else:
            for u in pending_users:
                row = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=10)
                row.pack(fill="x", padx=20, pady=5)

                info_text = f"User: {u['username']} | Email: {u['email']} | Company: {u['company'] or 'N/A'}"
                tk.Label(row, text=info_text, fg=theme["text"], bg=theme["card"], font=("Helvetica", 10)).pack(side="left")

                def approve(usr=u['username']):
                    database.set_user_status(usr, "approved")
                    self.log_safe(f"Admin approved account for '{usr}'.", "INFO")
                    messagebox.showinfo("Approved", f"Approved user {usr}")
                    self.render_admin_panel()

                def reject(usr=u['username']):
                    database.set_user_status(usr, "rejected")
                    self.log_safe(f"Admin rejected account for '{usr}'.", "WARN")
                    messagebox.showinfo("Rejected", f"Rejected user {usr}")
                    self.render_admin_panel()

                tk.Button(row, text="Approve", bg="#10b981", fg="white", font=("Helvetica", 9, "bold"), command=approve).pack(side="right", padx=5)
                tk.Button(row, text="Reject", bg="#ef4444", fg="white", font=("Helvetica", 9, "bold"), command=reject).pack(side="right")


if __name__ == "__main__":
    app = CyberShieldApp()
    app.mainloop()
