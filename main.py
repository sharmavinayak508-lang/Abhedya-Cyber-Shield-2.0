import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Import backend modules
from backend import database, auth, password_tools, file_tools, network_tools, logger, exporter, honeytoken

# Color themes configuration
THEMES = {
    "Dark Cyber": {
        "bg": "#0f172a",
        "sidebar": "#1e293b",
        "card": "#334155",
        "text": "#f8fafc",
        "accent": "#0ea5e9",
        "button": "#0284c7"
    },
    "Light Modern": {
        "bg": "#f8fafc",
        "sidebar": "#e2e8f0",
        "card": "#ffffff",
        "text": "#0f172a",
        "accent": "#0284c7",
        "button": "#0284c7"
    },
    "Matrix Green": {
        "bg": "#052e16",
        "sidebar": "#064e3b",
        "card": "#14532d",
        "text": "#f0fdf4",
        "accent": "#22c55e",
        "button": "#15803d"
    }
}

class CyberShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("INVINCIBLE CYBER SHIELD - Security Suite")
        self.geometry("1100x700")

        # Initialize Backend
        database.init_database()
        auth.ensure_default_user()

        self.login_guard = auth.LoginGuard()
        self.current_user = None
        self.current_theme = "Dark Cyber"

        # Background Image Handling
        self.bg_image_path = os.path.join(os.path.dirname(__file__), "bg.jpg")
        if not os.path.exists(self.bg_image_path):
            self.bg_image_path = os.path.join(os.path.dirname(__file__), "bg.png")

        # Container Frame
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Start with Login Screen
        self.show_login_screen()

    # ================= HELPER FOR BACKGROUND IMAGE =================
    def apply_background(self, parent_frame):
        if os.path.exists(self.bg_image_path):
            try:
                raw_img = Image.open(self.bg_image_path)
                resized_img = raw_img.resize((1100, 700), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(resized_img)

                bg_label = tk.Label(parent_frame, image=self.bg_photo)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Background render note: {e}")

    # ================= AUTHENTICATION SCREENS =================
    def show_login_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container, bg="#0f172a")
        frame.pack(fill="both", expand=True)

        # Render background logo
        self.apply_background(frame)

        # Overlay Glassmorphism Box
        box = tk.Frame(frame, bg="#0f172a", padx=35, pady=35, highlightbackground="#0ea5e9", highlightthickness=2)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="INVINCIBLE CYBER SHIELD", font=("Helvetica", 16, "bold"), fg="#0ea5e9", bg="#0f172a").pack(pady=(0, 5))
        tk.Label(box, text="PROTECTION ENGINE LOGIN", font=("Helvetica", 10), fg="#94a3b8", bg="#0f172a").pack(pady=(0, 15))

        tk.Label(box, text="Username", fg="#ffffff", bg="#0f172a", font=("Helvetica", 10, "bold")).pack(anchor="w")
        entry_user = tk.Entry(box, width=32, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", bd=1)
        entry_user.pack(pady=(2, 10))

        tk.Label(box, text="Password", fg="#ffffff", bg="#0f172a", font=("Helvetica", 10, "bold")).pack(anchor="w")
        entry_pass = tk.Entry(box, show="*", width=32, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", bd=1)
        entry_pass.pack(pady=(2, 10))

        lbl_msg = tk.Label(box, text="", fg="#ef4444", bg="#0f172a", font=("Helvetica", 9))
        lbl_msg.pack(pady=5)

        def do_login():
            user = entry_user.get()
            pwd = entry_pass.get()
            status, msg, user_data = self.login_guard.attempt(user, pwd)
            
            if status == "ok":
                self.current_user = user_data
                self.current_theme = user_data.get("theme", "Dark Cyber")
                logger.log_event(f"User '{user}' logged in successfully.", "INFO")
                self.show_dashboard_screen()
            else:
                lbl_msg.config(text=msg)

        tk.Button(box, text="AUTHORIZE ACCESS", bg="#0ea5e9", fg="white", font=("Helvetica", 10, "bold"), width=28, command=do_login, bd=0, py=6, cursor="hand2").pack(pady=8)
        tk.Button(box, text="Register New Account", bg="#334155", fg="white", width=28, command=self.show_register_screen, bd=0, py=5, cursor="hand2").pack()

    def show_register_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container, bg="#0f172a")
        frame.pack(fill="both", expand=True)

        self.apply_background(frame)

        box = tk.Frame(frame, bg="#0f172a", padx=35, pady=35, highlightbackground="#10b981", highlightthickness=2)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="NEW AGENT REGISTRATION", font=("Helvetica", 15, "bold"), fg="#10b981", bg="#0f172a").pack(pady=(0, 15))

        tk.Label(box, text="Choose Username", fg="#ffffff", bg="#0f172a", font=("Helvetica", 10, "bold")).pack(anchor="w")
        entry_user = tk.Entry(box, width=32, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", bd=1)
        entry_user.pack(pady=(2, 10))

        tk.Label(box, text="Choose Password", fg="#ffffff", bg="#0f172a", font=("Helvetica", 10, "bold")).pack(anchor="w")
        entry_pass = tk.Entry(box, show="*", width=32, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", bd=1)
        entry_pass.pack(pady=(2, 10))

        lbl_msg = tk.Label(box, text="", fg="#10b981", bg="#0f172a", font=("Helvetica", 9))
        lbl_msg.pack(pady=5)

        def do_register():
            user = entry_user.get()
            pwd = entry_pass.get()
            ok, msg = auth.register_user(user, pwd)
            lbl_msg.config(text=msg, fg="#10b981" if ok else "#ef4444")
            if ok:
                logger.log_event(f"New registration request submitted for '{user}'.", "WARN")

        tk.Button(box, text="SUBMIT REGISTRATION", bg="#10b981", fg="white", font=("Helvetica", 10, "bold"), width=28, command=do_register, bd=0, py=6, cursor="hand2").pack(pady=8)
        tk.Button(box, text="Back to Login", bg="#334155", fg="white", width=28, command=self.show_login_screen, bd=0, py=5, cursor="hand2").pack()

    # ================= MAIN DASHBOARD & NAVIGATION =================
    def show_dashboard_screen(self):
        self.clear_container()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        self.sidebar = tk.Frame(self.container, bg=theme["sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")

        self.main_content = tk.Frame(self.container, bg=theme["bg"])
        self.main_content.pack(side="right", fill="both", expand=True)

        tk.Label(self.sidebar, text="CYBER SHIELD", font=("Helvetica", 16, "bold"), fg=theme["accent"], bg=theme["sidebar"]).pack(pady=(20, 2))
        tk.Label(self.sidebar, text="PROTECTION ENGINE", font=("Helvetica", 8, "bold"), fg="#64748b", bg=theme["sidebar"]).pack(pady=(0, 20))

        pages = ["Dashboard", "File Analysis", "Password Vault", "AI Security Analyst", "Alerts", "Reports", "Settings"]
        if self.current_user and self.current_user.get("role") == "admin":
            pages.insert(1, "Admin Panel")

        for page in pages:
            btn = tk.Button(
                self.sidebar, text=page, anchor="w", padx=20, pady=8,
                bg=theme["sidebar"], fg=theme["text"], bd=0, font=("Helvetica", 10, "bold"),
                activebackground=theme["card"], activeforeground=theme["accent"],
                command=lambda p=page: self.load_page(p), cursor="hand2"
            )
            btn.pack(fill="x")

        tk.Button(self.sidebar, text="LOG OUT", bg="#ef4444", fg="white", bd=0, font=("Helvetica", 10, "bold"), py=8, command=self.show_login_screen, cursor="hand2").pack(side="bottom", fill="x", pady=20)

        self.load_page("Dashboard")

    def load_page(self, name):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        if name == "Dashboard":
            self.render_dashboard()
        elif name == "Admin Panel":
            self.render_admin_panel()
        elif name == "File Analysis":
            self.render_file_analysis()
        elif name == "Password Vault":
            self.render_password_vault()
        elif name == "AI Security Analyst":
            self.render_ai_analyst()
        elif name == "Alerts":
            self.render_alerts()
        elif name == "Reports":
            self.render_reports()
        elif name == "Settings":
            self.render_settings()

    # ================= FEATURE SCREENS =================
    def render_dashboard(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="System Threat & Security Dashboard", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        info = network_tools.get_host_info()
        card = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        card.pack(fill="x", padx=20, pady=5)

        tk.Label(card, text="Protected Network Telemetry", font=("Helvetica", 12, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w")
        tk.Label(card, text=f"Hostname: {info['hostname']}  |  Local IP: {info['local_ip']}  |  Route IP: {info['route_ip']}", fg=theme["text"], bg=theme["card"]).pack(anchor="w", pady=5)

        logs_card = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        logs_card.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(logs_card, text="Real-Time Malware Detection & Event Feed", font=("Helvetica", 12, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w", pady=(0, 5))
        
        logs = database.fetch_logs(limit=10)
        for log in logs:
            tk.Label(logs_card, text=f"[{log[1]}] [{log[2]}] {log[3]}", fg=theme["text"], bg=theme["card"], font=("Consolas", 9)).pack(anchor="w")

    def render_admin_panel(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Admin User Verification Panel", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        pending_users = database.fetch_pending_users()

        if not pending_users:
            tk.Label(self.main_content, text="No pending registration requests requiring authorization.", fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20)
            return

        for u in pending_users:
            row = tk.Frame(self.main_content, bg=theme["card"], padx=10, pady=10)
            row.pack(fill="x", padx=20, pady=5)

            tk.Label(row, text=f"Agent: {u['username']}  |  Role: {u['role']}", fg=theme["text"], bg=theme["card"], font=("Helvetica", 11)).pack(side="left")

            def approve(username=u['username']):
                database.set_user_status(username, "approved")
                logger.log_event(f"Admin approved account for '{username}'.", "INFO")
                messagebox.showinfo("Success", f"Approved user {username}")
                self.load_page("Admin Panel")

            def reject(username=u['username']):
                database.set_user_status(username, "rejected")
                logger.log_event(f"Admin rejected account for '{username}'.", "WARN")
                messagebox.showinfo("Rejected", f"Rejected user {username}")
                self.load_page("Admin Panel")

            tk.Button(row, text="Approve", bg="#10b981", fg="white", command=approve).pack(side="right", padx=5)
            tk.Button(row, text="Reject", bg="#ef4444", fg="white", command=reject).pack(side="right")

    def render_file_analysis(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="File Integrity & Malware Scanner", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        box.pack(fill="x", padx=20)

        lbl_file = tk.Label(box, text="No file selected", fg=theme["text"], bg=theme["card"])
        lbl_file.pack(anchor="w", pady=5)

        lbl_res = tk.Label(box, text="", fg=theme["accent"], bg=theme["card"], font=("Consolas", 10))
        lbl_res.pack(anchor="w", pady=5)

        selected_path = {"path": None}

        def choose_file():
            path = filedialog.askopenfilename()
            if path:
                selected_path["path"] = path
                lbl_file.config(text=f"File: {path}")

        def scan():
            if not selected_path["path"]:
                messagebox.showwarning("Warning", "Select a file first.")
                return
            res = file_tools.scan_file(selected_path["path"])
            threat_str = f"Threat: {res['threat']}" if res['threat'] else "Clean file (No match found)."
            lbl_res.config(text=f"SHA256: {res['sha256']}\nSize: {res['size']} bytes\nStatus: {threat_str}")

        def shred():
            if not selected_path["path"]:
                return
            if messagebox.askyesno("Confirm", "Are you sure you want to shred this file permanently?"):
                ok = file_tools.shred_file(selected_path["path"])
                messagebox.showinfo("Result", "File shredded successfully." if ok else "Shredding failed.")
                lbl_file.config(text="No file selected")

        tk.Button(box, text="Select File", bg=theme["button"], fg="white", command=choose_file).pack(side="left", padx=5)
        tk.Button(box, text="Scan File Signature", bg="#10b981", fg="white", command=scan).pack(side="left", padx=5)
        tk.Button(box, text="Shred File", bg="#ef4444", fg="white", command=shred).pack(side="left", padx=5)

    def render_password_vault(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Password Vault & Generator", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        box.pack(fill="x", padx=20)

        tk.Label(box, text="Generate & Test Cryptographic Password", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

        entry_gen = tk.Entry(box, font=("Consolas", 12), width=35)
        entry_gen.pack(anchor="w", pady=10)

        lbl_score = tk.Label(box, text="Strength: -", fg=theme["text"], bg=theme["card"])
        lbl_score.pack(anchor="w")

        def generate():
            pwd = password_tools.generate_password(16)
            analysis = password_tools.analyze_password(pwd)
            entry_gen.delete(0, tk.END)
            entry_gen.insert(0, pwd)
            lbl_score.config(text=f"Strength: {analysis['label']} ({analysis['entropy_bits']} bits entropy)")

        def test_pwd():
            pwd = entry_gen.get()
            analysis = password_tools.analyze_password(pwd)
            lbl_score.config(text=f"Strength: {analysis['label']} ({analysis['entropy_bits']} bits entropy)")

        tk.Button(box, text="Generate Password", bg=theme["button"], fg="white", command=generate).pack(side="left", pady=10, padx=5)
        tk.Button(box, text="Check Strength", bg="#10b981", fg="white", command=test_pwd).pack(side="left", pady=10)

    def render_ai_analyst(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="AI Security Analyst", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        box.pack(fill="both", expand=True, padx=20, pady=5)

        txt = tk.Text(box, bg=theme["bg"], fg=theme["text"], font=("Consolas", 10))
        txt.pack(fill="both", expand=True)

        txt.insert("end", "[AI Analyst] Initializing system rules assessment...\n")
        
        if honeytoken.sentinel.active:
            txt.insert("end", "[+] Canary Honeytoken Sentinel: ACTIVE\n")
        else:
            txt.insert("end", "[-] Canary Honeytoken Sentinel: INACTIVE (Deploying decoy file...)\n")
            honeytoken.sentinel.deploy()
            txt.insert("end", "[+] Decoy AWS credential honeypot deployed successfully.\n")

        txt.insert("end", "[+] PBKDF2 Password Iterations: 200,000 (Secure)\n")
        txt.insert("end", "[+] System recommendation: Regularly audit pending registration queues.\n")

    def render_alerts(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Live Network & Connection Alerts", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        card = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        card.pack(fill="both", expand=True, padx=20, pady=5)

        conns, err = network_tools.get_connections(limit=15)
        if err:
            tk.Label(card, text=f"Network Error: {err}", fg="#ef4444", bg=theme["card"]).pack(anchor="w")
        else:
            tk.Label(card, text="Active Network Connections:", font=("Helvetica", 11, "bold"), fg=theme["accent"], bg=theme["card"]).pack(anchor="w")
            for c in conns:
                tk.Label(card, text=f"{c[0]}:{c[1]} --> {c[2]}:{c[3]} [{c[4]}]", fg=theme["text"], bg=theme["card"], font=("Consolas", 9)).pack(anchor="w")

    def render_reports(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Security Reports & Logs Export", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        box.pack(fill="x", padx=20)

        logs = database.fetch_logs(limit=500)
        tk.Label(box, text=f"Total Recorded Log Entries: {len(logs)}", fg=theme["text"], bg=theme["card"], font=("Helvetica", 11)).pack(anchor="w", pady=5)

        def do_export():
            path = exporter.export_logs_csv(logs)
            messagebox.showinfo("Export Complete", f"CSV Log Report saved to:\n{path}")

        tk.Button(box, text="Export CSV Report", bg=theme["button"], fg="white", command=do_export).pack(anchor="w", pady=10)

    def render_settings(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Settings & Theme Options", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=15)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=15, pady=15)
        box.pack(fill="x", padx=20)

        tk.Label(box, text="Select Theme", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w", pady=5)

        selected_theme = tk.StringVar(value=self.current_theme)
        dropdown = ttk.Combobox(box, textvariable=selected_theme, values=list(THEMES.keys()), state="readonly")
        dropdown.pack(anchor="w", pady=5)

        def save_theme():
            new_theme = selected_theme.get()
            self.current_theme = new_theme
            database.update_user_theme(self.current_user["username"], new_theme)
            self.show_dashboard_screen()
            self.load_page("Settings")

        tk.Button(box, text="Apply Theme", bg=theme["button"], fg="white", command=save_theme).pack(anchor="w", pady=10)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = CyberShieldApp()
    app.mainloop()
