"""Password checker, generator and account settings."""
import tkinter as tk
from tkinter import messagebox

from backend import auth, password_tools
from backend.logger import log_event
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, entry, label, panel

LEVEL_COLORS = {"critical": T["accent_magenta"], "weak": T["accent_orange"],
                "good": T["accent_cyan"], "strong": T["accent_lime"], "empty": T["text_muted"]}


class PasswordPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        label(self, "PASSWORD TOOLKIT", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        wrap = tk.Frame(self, bg=T["bg_dark"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)

        # --- checker
        cp = panel(wrap, "STRENGTH CHECKER (updates as you type)", T["accent_cyan"])
        cp.pack(fill=tk.X, padx=5, pady=5)
        self.pwd = entry(cp, show="*", width=46)
        self.pwd.pack(pady=(10, 4))
        self.pwd.bind("<KeyRelease>", lambda _e: self.analyze())
        self.show = tk.BooleanVar(value=False)
        tk.Checkbutton(cp, text="Show password", variable=self.show, command=self.toggle,
                       fg=T["text_main"], bg=T["bg_dark"], selectcolor=T["bg_terminal"],
                       activebackground=T["bg_dark"], font=("Consolas", 9)).pack()
        self.meter = label(cp, "NO INPUT", T["text_muted"], 12, True)
        self.meter.pack(pady=2)
        self.entropy = label(cp, "", T["text_muted"], 9)
        self.entropy.pack()
        self.feedback = label(cp, "", T["text_main"], 9, justify=tk.LEFT)
        self.feedback.pack(pady=(2, 10))

        # --- generator
        gp = panel(wrap, "SECURE PASSWORD GENERATOR", T["accent_magenta"])
        gp.pack(fill=tk.X, padx=5, pady=5)
        row = tk.Frame(gp, bg=T["bg_dark"])
        row.pack(pady=8)
        label(row, "Length:").pack(side=tk.LEFT)
        self.length = tk.Spinbox(row, from_=12, to=64, width=5, justify="center", bg=T["bg_terminal"],
                                 fg=T["accent_lime"], font=("Consolas", 10))
        self.length.delete(0, tk.END)
        self.length.insert(0, "16")
        self.length.pack(side=tk.LEFT, padx=8)
        button(row, "GENERATE", self.generate, T["accent_magenta"]).pack(side=tk.LEFT, padx=3)
        button(row, "COPY", self.copy).pack(side=tk.LEFT, padx=3)
        self.generated = entry(gp, width=46, justify="center")
        self.generated.pack(pady=(0, 10))

        # --- account
        ap = panel(wrap, "ACCOUNT: CHANGE LOGIN PASSWORD", T["accent_orange"])
        ap.pack(fill=tk.X, padx=5, pady=5)
        row = tk.Frame(ap, bg=T["bg_dark"])
        row.pack(pady=8)
        label(row, "Current:").pack(side=tk.LEFT)
        self.old = entry(row, show="*", width=16)
        self.old.pack(side=tk.LEFT, padx=6)
        label(row, "New:").pack(side=tk.LEFT)
        self.new = entry(row, show="*", width=16)
        self.new.pack(side=tk.LEFT, padx=6)
        button(row, "UPDATE", self.change, T["accent_orange"]).pack(side=tk.LEFT, padx=3)

    def toggle(self):
        self.pwd.config(show="" if self.show.get() else "*")

    def analyze(self):
        res = password_tools.analyze_password(self.pwd.get())
        self.meter.config(text=res["label"], fg=LEVEL_COLORS[res["level"]])
        self.entropy.config(text=f"Estimated entropy: {res['entropy_bits']} bits" if res["entropy_bits"] else "")
        self.feedback.config(text="\n".join("- " + f for f in res["feedback"]) or
                             ("Looks good." if self.pwd.get() else ""))

    def generate(self):
        try:
            length = int(self.length.get())
        except ValueError:
            length = 16
        self.generated.delete(0, tk.END)
        self.generated.insert(0, password_tools.generate_password(length))
        log_event("Generated a secure random password.", "INFO")

    def copy(self):
        value = self.generated.get()
        if value:
            self.clipboard_clear()
            self.clipboard_append(value)

    def change(self):
        ok, msg = auth.change_password(self.app.username, self.old.get(), self.new.get())
        self.old.delete(0, tk.END)
        self.new.delete(0, tk.END)
        if ok:
            log_event(f"Password changed for '{self.app.username}'.", "INFO")
        (messagebox.showinfo if ok else messagebox.showwarning)("Account", msg)
