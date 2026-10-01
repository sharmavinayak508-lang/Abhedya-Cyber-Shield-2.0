"""Searchable log history stored in SQLite, with CSV export."""
import tkinter as tk
from tkinter import messagebox, ttk

from backend import database, exporter
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, entry, label, panel, table

SEV_TAGS = {"CRITICAL": T["accent_magenta"], "ERROR": "#ff6688", "WARN": T["accent_orange"], "INFO": T["accent_lime"]}


class LogsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.rows = []
        label(self, "LOG HISTORY", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        bar = tk.Frame(self, bg=T["bg_dark"])
        bar.pack(fill=tk.X, padx=14, pady=4)
        label(bar, "Severity:").pack(side=tk.LEFT)
        self.severity = ttk.Combobox(bar, values=["ALL", "INFO", "WARN", "ERROR", "CRITICAL"], width=10, state="readonly")
        self.severity.set("ALL")
        self.severity.pack(side=tk.LEFT, padx=6)
        label(bar, "Search:").pack(side=tk.LEFT, padx=(10, 0))
        self.search = entry(bar, width=24)
        self.search.pack(side=tk.LEFT, padx=6)
        self.search.bind("<Return>", lambda _e: self.refresh())
        button(bar, "APPLY", self.refresh).pack(side=tk.LEFT, padx=3)
        button(bar, "EXPORT CSV", self.export, T["accent_lime"]).pack(side=tk.RIGHT, padx=3)

        box = panel(self, "SECURITY EVENTS (newest first, max 500)", T["accent_lime"])
        box.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)
        self.tree = table(box, [("id", "ID", 50), ("time", "TIME", 160), ("sev", "SEVERITY", 90), ("msg", "MESSAGE", 600)])
        for sev, color in SEV_TAGS.items():
            self.tree.tag_configure(sev, foreground=color)

    def on_show(self):
        self.refresh()

    def refresh(self):
        self.rows = database.fetch_logs(self.severity.get(), self.search.get().strip())
        self.tree.delete(*self.tree.get_children())
        for row in self.rows:
            self.tree.insert("", tk.END, values=row, tags=(row[2],))

    def export(self):
        if not self.rows:
            messagebox.showinfo("Nothing to export", "No log rows match the current filter.")
            return
        path = exporter.export_logs_csv(self.rows)
        messagebox.showinfo("Exported", f"Saved:\n{path}")
