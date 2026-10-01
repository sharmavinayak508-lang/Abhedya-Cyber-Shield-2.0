"""Base class for every dashboard page."""
import tkinter as tk

from config import THEME as T


class Page(tk.Frame):
    """A screen inside the dashboard. Override the hooks you need."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=T["bg_dark"])
        self.app = app
        self.visible = False

    def on_show(self):
        """Called each time the page becomes visible."""

    def on_hide(self):
        """Called when another page replaces this one."""

    def on_new_logs(self, items):
        """Called with new log events (even when the page is hidden)."""
