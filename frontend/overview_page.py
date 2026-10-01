"""Overview: security score gauge, live CPU/RAM chart, severity bars, live feed."""
import tkinter as tk

from backend import logger, security_score
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import BarChart, Gauge, LineChart, append_text, label, panel, text_box

SEVERITY_COLORS = {"INFO": T["accent_cyan"], "WARN": T["accent_orange"],
                   "ERROR": "#ff6688", "CRITICAL": T["accent_magenta"]}


class OverviewPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.counts = {k: 0 for k in SEVERITY_COLORS}

        label(self, "SECURITY OVERVIEW", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        top = tk.Frame(self, bg=T["bg_dark"])
        top.pack(fill=tk.X, padx=14)

        gp = panel(top, "SECURITY SCORE", T["accent_lime"])
        gp.pack(side=tk.LEFT, padx=5, pady=5)
        self.gauge = Gauge(gp, width=230, height=200)
        self.gauge.pack(padx=8, pady=8)

        cp = panel(top, "CPU / RAM (LIVE %)", T["accent_cyan"])
        cp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chart = LineChart(cp, {"CPU": T["accent_cyan"], "RAM": T["accent_magenta"]}, height=200)
        self.chart.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        bp = panel(top, "EVENTS BY SEVERITY", T["accent_orange"])
        bp.pack(side=tk.LEFT, padx=5, pady=5)
        self.bars = BarChart(bp, width=230, height=200)
        self.bars.pack(padx=8, pady=8)
        self._refresh_bars()

        feed = panel(self, "LIVE TELEMETRY FEED", T["accent_lime"])
        feed.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)
        self.feed = text_box(feed, T["accent_lime"])

    def _refresh_bars(self):
        self.bars.set_data([(k, self.counts[k], SEVERITY_COLORS[k]) for k in SEVERITY_COLORS])

    def update_stats(self, usage):
        """Called by the dashboard once per second."""
        if usage:
            self.chart.push(CPU=usage[0], RAM=usage[1])
        self.gauge.set_value(security_score.get_score())

    def on_show(self):
        self.gauge.set_value(security_score.get_score())

    def on_new_logs(self, items):
        for item in items:
            self.counts[item["severity"]] = self.counts.get(item["severity"], 0) + 1
            append_text(self.feed, logger.format_item(item))
        self._refresh_bars()
        self.gauge.set_value(security_score.get_score())
