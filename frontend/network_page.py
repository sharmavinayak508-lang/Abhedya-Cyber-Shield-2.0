"""Network: host info and a live map of remote connections."""
import math
import tkinter as tk

from backend import network_tools
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, font, label, panel, set_text, text_box


class NetworkPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._job = None
        self._conns, self._err = [], ""
        label(self, "NETWORK MONITOR", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        button(self, "REFRESH NOW", self.refresh).pack()

        top = tk.Frame(self, bg=T["bg_dark"])
        top.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)
        hp = panel(top, "HOST INFORMATION", T["accent_orange"])
        hp.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        hp.configure(width=300)
        hp.pack_propagate(False)
        self.info_box = text_box(hp, T["accent_orange"])

        mp = panel(top, "CONNECTION MAP (auto-refresh 5s)", T["accent_magenta"])
        mp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.canvas = tk.Canvas(mp, bg=T["bg_terminal"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda _e: self.draw())

        fp = panel(self, "CONNECTION FEED", T["accent_cyan"])
        fp.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))
        self.feed = text_box(fp, T["accent_cyan"], height=7)

    def on_show(self):
        self.refresh()
        if self._job is None:
            self._job = self.after(5000, self._loop)

    def _loop(self):
        self._job = None
        if self.visible and self.winfo_exists():
            self.refresh()
            self._job = self.after(5000, self._loop)

    def refresh(self):
        info = network_tools.get_host_info()
        lines = [f"Host name : {info['hostname']}", f"Local IP  : {info['local_ip']}",
                 f"Route IP  : {info['route_ip']}", "", "INTERFACES"]
        lines += [f" {name}: {ip}" for name, ip in info["interfaces"]] or [" (needs psutil)"]
        set_text(self.info_box, "\n".join(lines))
        self._conns, self._err = network_tools.get_connections()
        self.draw()
        feed = [f"LOCAL  {c[0]}:{c[1]}\nREMOTE {c[2]}:{c[3]}\nSTATE  {c[4]}\n" + "-" * 30 for c in self._conns]
        set_text(self.feed, "\n".join(feed) if feed else (self._err or "No active remote connections."))

    def draw(self):
        cv = self.canvas
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 100 or h < 100:
            return
        for x in range(0, w, 40):
            cv.create_line(x, 0, x, h, fill="#0b0f19")
        for y in range(0, h, 40):
            cv.create_line(0, y, w, y, fill="#0b0f19")
        cx, cy = w // 2, h // 2
        shown = self._conns[:12]
        radius = max(40, min(cx, cy) - 40)
        for i, c in enumerate(shown):
            ang = i / len(shown) * 2 * math.pi
            nx, ny = cx + int(radius * math.cos(ang)), cy + int(radius * math.sin(ang))
            cv.create_line(cx, cy, nx, ny, fill="#13243a")
            cv.create_oval(nx - 5, ny - 5, nx + 5, ny + 5, fill=T["accent_magenta"], outline="")
            cv.create_text(nx, ny + 14, text=f"{c[2]}:{c[3]}", fill=T["text_muted"], font=font(7))
        cv.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=T["accent_cyan"], outline="")
        cv.create_text(cx, cy - 18, text="LOCALHOST", fill="white", font=font(8, True))
        if not shown:
            cv.create_text(cx, cy + 40, text=self._err or "No active remote connections",
                           fill=T["text_muted"], font=font(9), width=w - 40)
