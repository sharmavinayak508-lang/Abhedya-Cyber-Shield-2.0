import tkinter as tk
from tkinter import ttk, messagebox

# Import backend modules
from backend import database, auth, password_tools

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
        self.title("CyberShield Security Suite")
        self.geometry("1100x650")

        # Initialize Backend
        database.init_database()
        auth.ensure_default_user()

        self.login_guard = auth.LoginGuard()
        self.current_user = None
        self.current_theme = "Dark Cyber"

        # Container Frame
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Start with Login Screen
        self.show_login_screen()

    def apply_theme_colors(self, widget, colors):
        """Recursively apply theme colors."""
        try:
            widget.configure(bg=colors["bg"])
        except tk.TclError:
            pass

    # ================= AUTHENTICATION SCREENS =================
    def show_login_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container, bg="#0f172a")
        frame.pack(fill="both", expand=True)

        box = tk.Frame(frame, bg="#1e293b", padx=30, pady=30)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="CyberShield Login", font=("Helvetica", 18, "bold"), fg="#0ea5e9", bg="#1e293b").pack(pady=10)

        tk.Label(box, text="Username", fg="#ffffff", bg="#1e293b").pack(anchor="w")
        entry_user = tk.Entry(box, width=30)
        entry_user.pack(pady=5)

        tk.Label(box, text="Password", fg="#ffffff", bg="#1e293b").pack(anchor="w")
        entry_pass = tk.Entry(box, show="*", width=30)
        entry_pass.pack(pady=5)

        lbl_msg = tk.Label(box, text="", fg="#ef4444", bg="#1e293b")
        lbl_msg.pack(pady=5)

        def do_login():
            user = entry_user.get()
            pwd = entry_pass.get()
            status, msg, user_data = self.login_guard.attempt(user, pwd)
            
            if status == "ok":
                self.current_user = user_data
                self.current_theme = user_data.get("theme", "Dark Cyber")
                self.show_dashboard_screen()
            else:
                lbl_msg.config(text=msg)

        tk.Button(box, text="Log In", bg="#0ea5e9", fg="white", font=("Helvetica", 10, "bold"), width=25, command=do_login).pack(pady=10)
        tk.Button(box, text="Create Account (Register)", bg="#334155", fg="white", width=25, command=self.show_register_screen).pack()

    def show_register_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container, bg="#0f172a")
        frame.pack(fill="both", expand=True)

        box = tk.Frame(frame, bg="#1e293b", padx=30, pady=30)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="Register New Account", font=("Helvetica", 16, "bold"), fg="#0ea5e9", bg="#1e293b").pack(pady=10)

        tk.Label(box, text="Choose Username", fg="#ffffff", bg="#1e293b").pack(anchor="w")
        entry_user = tk.Entry(box, width=30)
        entry_user.pack(pady=5)

        tk.Label(box, text="Choose Password", fg="#ffffff", bg="#1e293b").pack(anchor="w")
        entry_pass = tk.Entry(box, show="*", width=30)
        entry_pass.pack(pady=5)

        lbl_msg = tk.Label(box, text="", fg="#10b981", bg="#1e293b")
        lbl_msg.pack(pady=5)

        def do_register():
            user = entry_user.get()
            pwd = entry_pass.get()
            ok, msg = auth.register_user(user, pwd)
            lbl_msg.config(text=msg, fg="#10b981" if ok else "#ef4444")

        tk.Button(box, text="Submit Registration", bg="#10b981", fg="white", font=("Helvetica", 10, "bold"), width=25, command=do_register).pack(pady=10)
        tk.Button(box, text="Back to Login", bg="#334155", fg="white", width=25, command=self.show_login_screen).pack()

    # ================= MAIN APPLICATION DASHBOARD =================
    def show_dashboard_screen(self):
        self.clear_container()
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        # Layout Split: Sidebar + Main Content Area
        self.sidebar = tk.Frame(self.container, bg=theme["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")

        self.main_content = tk.Frame(self.container, bg=theme["bg"])
        self.main_content.pack(side="right", fill="both", expand=True)

        # Header Title in Sidebar
        tk.Label(self.sidebar, text="CyberShield", font=("Helvetica", 16, "bold"), fg=theme["accent"], bg=theme["sidebar"]).pack(pady=20)

        # Navigation Options
        pages = ["Dashboard", "File Analysis", "Password Vault", "AI Security Analyst", "Alerts", "Reports", "Settings"]
        
        # Add Admin Panel only if account role is admin
        if self.current_user and self.current_user.get("role") == "admin":
            pages.insert(1, "Admin Panel")

        for page in pages:
            btn = tk.Button(
                self.sidebar, text=page, anchor="w", padx=20, pady=8,
                bg=theme["sidebar"], fg=theme["text"], bd=0, font=("Helvetica", 11),
                command=lambda p=page: self.load_page(p)
            )
            btn.pack(fill="x")

        # Logout Button at bottom
        tk.Button(self.sidebar, text="Log Out", bg="#ef4444", fg="white", bd=0, command=self.show_login_screen).pack(side="bottom", fill="x", pady=20)

        self.load_page("Dashboard")

    def load_page(self, name):
        """Page Router."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])

        if name == "Dashboard":
            tk.Label(self.main_content, text="Security Dashboard", font=("Helvetica", 20, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", pading=20, padx=20, pady=20)
            tk.Label(self.main_content, text=f"Welcome back, {self.current_user['username']}! (Role: {self.current_user['role']})", fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20)

        elif name == "Admin Panel":
            self.render_admin_panel()

        elif name == "Password Vault":
            self.render_password_vault()

        elif name == "Settings":
            self.render_settings()

        else:
            tk.Label(self.main_content, text=f"{name} Page", font=("Helvetica", 20, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=20)
            tk.Label(self.main_content, text="Page modules active and running.", fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20)

    # ================= FEATURE SCREENS =================
    def render_admin_panel(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Admin Approval Panel", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=20)

        pending_users = database.fetch_pending_users()

        if not pending_users:
            tk.Label(self.main_content, text="No registration requests pending approval.", fg=theme["text"], bg=theme["bg"]).pack(anchor="w", padx=20)
            return

        for u in pending_users:
            row = tk.Frame(self.main_content, bg=theme["card"], padx=10, pady=10)
            row.pack(fill="x", padx=20, pady=5)

            tk.Label(row, text=f"User: {u['username']} | Role: {u['role']}", fg=theme["text"], bg=theme["card"], font=("Helvetica", 11)).pack(side="left")

            def approve(username=u['username']):
                database.set_user_status(username, "approved")
                messagebox.showinfo("Success", f"Approved user {username}")
                self.load_page("Admin Panel")

            def reject(username=u['username']):
                database.set_user_status(username, "rejected")
                messagebox.showinfo("Rejected", f"Rejected user {username}")
                self.load_page("Admin Panel")

            tk.Button(row, text="Approve", bg="#10b981", fg="white", command=approve).pack(side="right", padx=5)
            tk.Button(row, text="Reject", bg="#ef4444", fg="white", command=reject).pack(side="right")

    def render_password_vault(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Password Vault & Generator", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=20)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
        box.pack(fill="x", padx=20)

        tk.Label(box, text="Generate Strong Password", font=("Helvetica", 12, "bold"), fg=theme["text"], bg=theme["card"]).pack(anchor="w")

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

        tk.Button(box, text="Generate Password", bg=theme["button"], fg="white", command=generate).pack(anchor="w", pady=10)

    def render_settings(self):
        theme = THEMES.get(self.current_theme, THEMES["Dark Cyber"])
        tk.Label(self.main_content, text="Settings & Theme", font=("Helvetica", 18, "bold"), fg=theme["accent"], bg=theme["bg"]).pack(anchor="w", padx=20, pady=20)

        box = tk.Frame(self.main_content, bg=theme["card"], padx=20, pady=20)
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
