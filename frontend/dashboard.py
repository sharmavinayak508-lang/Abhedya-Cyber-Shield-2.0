"""Main window: sidebar navigation plus stacked pages."""
import tkinter as tk

from backend import crypto, logger, security_score, system_stats
from backend.honeytoken import sentinel
from backend.logger import log_event
from config import APP_NAME, THEME as T
from frontend.files_page import FilesPage
from frontend.logs_page import LogsPage
from frontend.network_page import NetworkPage
from frontend.overview_page import OverviewPage
from frontend.password_page import PasswordPage
from frontend.process_page import ProcessPage
from frontend.vault_page import VaultPage
from frontend.widgets import apply_styles, font

NAV = [
    ("overview", "OVERVIEW", OverviewPage),
    ("files", "FILE SECURITY", FilesPage),
    ("processes", "PROCESSES", ProcessPage),
    ("network", "NETWORK", NetworkPage),
    ("vault", "VAULT & TRAPS", VaultPage),
    ("passwords", "PASSWORDS", PasswordPage),
    ("logs", "LOGS", LogsPage),
]


class Dashboard:
    def __init__(self, root, username, on_logout):
        self.root, self.username, self.on_logout = root, username, on_logout
        root.title(f"{APP_NAME} - Security Operations Center")
        root.resizable(True, True)
        root.geometry("1120x700")
        root.minsize(980, 620)
        apply_styles(root)

        self.frame = tk.Frame(root, bg=T["bg_dark"])
        self.frame.pack(fill=tk.BOTH, expand=True)
        side = tk.Frame(self.frame, bg=T["bg_panel"], width=190)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)
        tk.Label(side, text=APP_NAME.upper(), fg=T["accent_cyan"], bg=T["bg_panel"], font=font(14, True)).pack(pady=(20, 2))
        tk.Label(side, text=f"operator: {username}", fg=T["text_muted"], bg=T["bg_panel"], font=font(8)).pack(pady=(0, 18))

        self.content = tk.Frame(self.frame, bg=T["bg_dark"])
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.pages, self.nav_buttons, self.current = {}, {}, None
        for key, title, cls in NAV:
            page = cls(self.content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[key] = page
            btn = tk.Button(side, text=f"  {title}", anchor="w", bg=T["bg_panel"], fg=T["text_main"],
                            activebackground=T["accent_purple"], activeforeground="white", font=font(10, True),
                            bd=0, cursor="hand2", pady=8, command=lambda k=key: self.show(k))
            btn.pack(fill=tk.X, padx=8, pady=2)
            self.nav_buttons[key] = btn
        tk.Button(side, text="  SIGN OUT", anchor="w", bg=T["bg_panel"], fg=T["accent_magenta"],
                  activebackground=T["accent_magenta"], activeforeground="white", font=font(10, True),
                  bd=0, cursor="hand2", pady=8, command=self.logout).pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=14)

        root.protocol("WM_DELETE_WINDOW", self.close)
        log_event("Operations environment established.", "INFO")
        self.show("overview")
        self._ticks = 0
        self._fast()
        self._slow()

    def show(self, key):
        if self.current:
            self.pages[self.current].visible = False
            self.pages[self.current].on_hide()
        self.current = key
        page = self.pages[key]
        page.tkraise()
        page.visible = True
        page.on_show()
        for k, btn in self.nav_buttons.items():
            btn.config(bg=T["accent_purple"] if k == key else T["bg_panel"])

    def _fast(self):
        """Every 300 ms: move queued events to the UI and the database."""
        if not self.frame.winfo_exists():
            return
        items = logger.drain_queue()
        if items:
            for page in self.pages.values():
                page.on_new_logs(items)
        self.root.after(300, self._fast)

    def _slow(self):
        """Every second: live stats; every 30 s: slowly restore the score."""
        if not self.frame.winfo_exists():
            return
        self._ticks += 1
        if self._ticks % 30 == 0:
            security_score.recover(1)
        self.pages["overview"].update_stats(system_stats.get_usage())
        self.root.after(1000, self._slow)

    def logout(self):
        crypto.lock_vault()
        logger.drain_queue()
        self.frame.destroy()
        self.on_logout()

    def close(self):
        sentinel.stop()
        crypto.lock_vault()
        logger.drain_queue()
        self.root.destroy()
