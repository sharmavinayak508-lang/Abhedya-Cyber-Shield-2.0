"""Reusable themed Tkinter widgets, charts and helpers."""
import queue
import threading
import tkinter as tk
from tkinter import ttk

from backend import security_score
from config import THEME as T


def font(size=9, bold=False):
    return (T["font_family"], size, "bold" if bold else "normal")


def apply_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", background=T["bg_terminal"], fieldbackground=T["bg_terminal"],
                    foreground=T["text_main"], rowheight=22, borderwidth=0, font=font(9))
    style.configure("Treeview.Heading", background=T["bg_panel"], foreground=T["accent_cyan"],
                    font=font(9, True), borderwidth=0)
    style.map("Treeview", background=[("selected", T["accent_purple"])])
    style.configure("Vertical.TScrollbar", background=T["bg_panel"], troughcolor=T["bg_dark"],
                    bordercolor=T["bg_dark"], arrowcolor=T["accent_cyan"])
    style.configure("TCombobox", fieldbackground=T["bg_terminal"], background=T["bg_panel"],
                    foreground=T["accent_lime"], arrowcolor=T["accent_cyan"])


def label(parent, text, color=None, size=9, bold=False, **kw):
    return tk.Label(parent, text=text, fg=color or T["text_main"], bg=T["bg_dark"], font=font(size, bold), **kw)


def button(parent, text, command, color=None, **kw):
    color = color or T["accent_cyan"]
    options = dict(bg=T["bg_panel"], fg=color, activebackground=color, activeforeground="black",
                   font=font(9, True), bd=1, relief=tk.SOLID, cursor="hand2", padx=10, pady=4)
    options.update(kw)  # callers may override padding etc.
    return tk.Button(parent, text=text, command=command, **options)


def entry(parent, show=None, color=None, width=30, **kw):
    return tk.Entry(parent, show=show, width=width, bg=T["bg_terminal"], fg=color or T["accent_lime"],
                    insertbackground=color or T["accent_lime"], font=font(10), bd=1, relief=tk.SOLID, **kw)


def panel(parent, title, color=None):
    return tk.LabelFrame(parent, text=f" {title} ", fg=color or T["accent_cyan"], bg=T["bg_dark"],
                         font=font(9, True), bd=1, relief=tk.SOLID)


def text_box(parent, color=None, height=8):
    """Read-only scrolling text area (packed into parent). Use set_text/append_text."""
    frame = tk.Frame(parent, bg=T["bg_dark"])
    frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
    sb = ttk.Scrollbar(frame, orient="vertical")
    box = tk.Text(frame, height=height, bg=T["bg_terminal"], fg=color or T["accent_lime"], font=font(9),
                  bd=0, wrap="word", state=tk.DISABLED, yscrollcommand=sb.set)
    sb.config(command=box.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return box


def set_text(box, content):
    box.config(state=tk.NORMAL)
    box.delete("1.0", tk.END)
    box.insert(tk.END, content)
    box.config(state=tk.DISABLED)


def append_text(box, line, max_lines=500):
    box.config(state=tk.NORMAL)
    box.insert(tk.END, line + "\n")
    if int(box.index("end-1c").split(".")[0]) > max_lines:
        box.delete("1.0", "50.0")
    box.see(tk.END)
    box.config(state=tk.DISABLED)


def table(parent, columns):
    """columns: list of (id, heading, width). Returns the ttk.Treeview."""
    frame = tk.Frame(parent, bg=T["bg_dark"])
    frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings")
    for cid, heading, width in columns:
        tree.heading(cid, text=heading)
        tree.column(cid, width=width, anchor="w")
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return tree


def run_async(widget, func, on_done, poll_ms=150):
    """Run func() in a thread; call on_done(ok, result_or_exception) on the UI thread."""
    results = queue.Queue()

    def worker():
        try:
            results.put((True, func()))
        except Exception as exc:  # noqa: BLE001 - reported to the UI
            results.put((False, exc))

    threading.Thread(target=worker, daemon=True).start()

    def poll():
        try:
            ok, value = results.get_nowait()
        except queue.Empty:
            if widget.winfo_exists():
                widget.after(poll_ms, poll)
            return
        if widget.winfo_exists():
            on_done(ok, value)

    widget.after(poll_ms, poll)


# ---------------------------------------------------------------- charts
class Gauge(tk.Canvas):
    """Semi-circular security score gauge."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=T["bg_terminal"], highlightthickness=0, **kw)
        self.value = 100
        self.bind("<Configure>", lambda _e: self.redraw())

    def set_value(self, value):
        if value != self.value:
            self.value = value
            self.redraw()

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 40 or h < 40:
            return
        size = min(w, h) - 40
        x0, y0 = (w - size) / 2, (h - size) / 2 - 8
        text, color = security_score.get_label(self.value)
        self.create_arc(x0, y0, x0 + size, y0 + size, start=210, extent=-240, style=tk.ARC,
                        width=14, outline="#12151f")
        if self.value > 0:
            self.create_arc(x0, y0, x0 + size, y0 + size, start=210, extent=-240 * self.value / 100,
                            style=tk.ARC, width=14, outline=color)
        self.create_text(w / 2, y0 + size / 2, text=str(self.value), fill=color, font=font(28, True))
        self.create_text(w / 2, h - 18, text=text, fill=color, font=font(10, True))


class LineChart(tk.Canvas):
    """Rolling multi-series line chart for values 0-100."""

    def __init__(self, parent, series, max_points=60, **kw):
        super().__init__(parent, bg=T["bg_terminal"], highlightthickness=0, **kw)
        self.colors = series
        self.data = {name: [] for name in series}
        self.max_points = max_points
        self.bind("<Configure>", lambda _e: self.redraw())

    def push(self, **values):
        for name, value in values.items():
            self.data[name].append(value)
            del self.data[name][:-self.max_points]
        self.redraw()

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60 or h < 60:
            return
        pad = 28
        for pct in (0, 25, 50, 75, 100):
            y = h - pad - pct / 100 * (h - 2 * pad)
            self.create_line(pad, y, w - 10, y, fill="#0b0f19")
            self.create_text(pad - 4, y, text=str(pct), fill=T["text_muted"], font=font(7), anchor="e")
        step = (w - pad - 10) / (self.max_points - 1)
        legend_x = pad + 6
        for name, color in self.colors.items():
            values = self.data[name]
            if len(values) >= 2:
                pts = []
                for i, v in enumerate(values):
                    pts += [pad + i * step, h - pad - v / 100 * (h - 2 * pad)]
                self.create_line(*pts, fill=color, width=2)
            self.create_text(legend_x, 10, text=name, fill=color, font=font(8, True), anchor="w")
            legend_x += 60
        if not any(self.data.values()):
            self.create_text(w / 2, h / 2, text="Waiting for data (needs psutil)...", fill=T["text_muted"], font=font(9))


class BarChart(tk.Canvas):
    """Vertical bars: data is a list of (label, count, colour)."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=T["bg_terminal"], highlightthickness=0, **kw)
        self.data = []
        self.bind("<Configure>", lambda _e: self.redraw())

    def set_data(self, data):
        self.data = data
        self.redraw()

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 60 or h < 60 or not self.data:
            return
        top = max(1, max(c for _l, c, _col in self.data))
        slot = (w - 20) / len(self.data)
        for i, (name, count, color) in enumerate(self.data):
            x0 = 10 + i * slot + slot * 0.18
            x1 = 10 + (i + 1) * slot - slot * 0.18
            bar_h = (h - 50) * count / top
            self.create_rectangle(x0, h - 28 - bar_h, x1, h - 28, fill=color, outline="")
            self.create_text((x0 + x1) / 2, h - 28 - bar_h - 8, text=str(count), fill=color, font=font(9, True))
            self.create_text((x0 + x1) / 2, h - 12, text=name, fill=T["text_muted"], font=font(7))
