"""Process auditor with simple suspicious-process rules."""
import tkinter as tk
from tkinter import messagebox

from backend import process_tools
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, label, panel, table


class ProcessPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        label(self, "PROCESS AUDITOR", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        if not process_tools.HAS_PSUTIL:
            label(self, "psutil is not installed.\nRun: pip install psutil", T["accent_magenta"], 11).pack(pady=40)
            self.tree = None
            return

        bar = tk.Frame(self, bg=T["bg_dark"])
        bar.pack(fill=tk.X, padx=14, pady=4)
        button(bar, "REFRESH", self.refresh).pack(side=tk.LEFT, padx=3)
        self.only_flagged = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="Show suspicious only", variable=self.only_flagged, command=self.refresh,
                       fg=T["text_main"], bg=T["bg_dark"], selectcolor=T["bg_terminal"],
                       activebackground=T["bg_dark"], activeforeground=T["accent_cyan"],
                       font=("Consolas", 9)).pack(side=tk.LEFT, padx=10)
        button(bar, "TERMINATE SELECTED", self.terminate, T["accent_magenta"]).pack(side=tk.RIGHT, padx=3)

        box = panel(self, "RUNNING PROCESSES (sorted by memory)", T["accent_lime"])
        box.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)
        self.tree = table(box, [("pid", "PID", 70), ("name", "NAME", 220), ("user", "USER", 180),
                                ("mem", "MEM %", 70), ("flag", "WARNING", 260)])
        self.tree.tag_configure("flag", foreground=T["accent_magenta"])

    def on_show(self):
        if self.tree is not None:
            self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for p in process_tools.list_processes():
            if self.only_flagged.get() and not p["flag"]:
                continue
            tags = ("flag",) if p["flag"] else ()
            self.tree.insert("", tk.END, values=(p["pid"], p["name"], p["user"], p["memory"], p["flag"]), tags=tags)

    def terminate(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select a process", "Click a process in the list first.")
            return
        pid, name = int(self.tree.item(sel[0], "values")[0]), self.tree.item(sel[0], "values")[1]
        if not messagebox.askyesno("Confirm", f"Terminate {name} (PID {pid})?\nUnsaved work in it will be lost."):
            return
        try:
            process_tools.terminate(pid)
            messagebox.showinfo("Done", f"{name} was asked to terminate.")
        except Exception as exc:
            messagebox.showerror("Failed", str(exc))
        self.refresh()
