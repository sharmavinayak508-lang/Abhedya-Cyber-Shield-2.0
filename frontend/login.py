"""Login screen with salted-hash verification and temporary lock-out."""
import tkinter as tk

from backend import auth
from backend.logger import log_event
from config import APP_NAME, THEME as T
from frontend.widgets import button, entry, label


class LoginFrame(tk.Frame):
    def __init__(self, root, on_success):
        super().__init__(root, bg=T["bg_dark"])
        self.on_success = on_success
        self.guard = auth.LoginGuard(max_attempts=3, lock_seconds=30)
        root.title(f"{APP_NAME} - Sign in")
        root.geometry("460x440")
        root.resizable(False, False)
        self.pack(fill=tk.BOTH, expand=True)

        label(self, f"{APP_NAME.upper()}", T["accent_cyan"], 20, True).pack(pady=(40, 0))
        label(self, "SECURITY OPERATIONS CENTER", T["text_muted"], 9).pack(pady=(0, 24))
        label(self, "Username").pack()
        self.user = entry(self, justify="center")
        self.user.pack(pady=6, ipady=3)
        self.user.insert(0, auth.DEFAULT_USER)
        label(self, "Password").pack()
        self.pw = entry(self, show="*", justify="center")
        self.pw.pack(pady=6, ipady=3)
        self.pw.focus_set()
        self.pw.bind("<Return>", lambda _e: self.submit())
        self.btn = button(self, "SIGN IN", self.submit, pady=6)
        self.btn.pack(pady=14)
        self.msg = label(self, "", T["accent_magenta"], 9)
        self.msg.pack()
        label(self, f"First run? Default login: {auth.DEFAULT_USER} / {auth.DEFAULT_PASSWORD}\n"
                    "Change it later on the PASSWORDS page.", T["text_muted"], 8).pack(side=tk.BOTTOM, pady=14)

    def submit(self):
        username = self.user.get().strip()
        status, message = self.guard.attempt(username, self.pw.get())
        self.pw.delete(0, tk.END)
        if status == "ok":
            log_event(f"User '{username}' signed in.", "INFO")
            self.destroy()
            self.on_success(username)
            return
        self.msg.config(text=message)
        if status == "locked":
            if "Too many" in message:
                log_event(f"Login lock-out after repeated failures for '{username}'.", "CRITICAL")
            self.btn.config(state=tk.DISABLED)
            self._countdown()
        else:
            log_event(f"Failed login attempt for '{username}'.", "WARN")

    def _countdown(self):
        if not self.winfo_exists():
            return
        left = self.guard.seconds_locked()
        if left > 0:
            self.msg.config(text=f"Locked. Try again in {left}s.")
            self.after(500, self._countdown)
        else:
            self.btn.config(state=tk.NORMAL)
            self.msg.config(text="")
