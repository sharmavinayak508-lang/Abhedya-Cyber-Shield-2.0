"""File security: hash auditor, PE analyzer and folder integrity monitor."""
import tkinter as tk
from tkinter import filedialog, messagebox

from backend import file_tools, integrity, pe_analyzer
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, label, panel, run_async, set_text, text_box


class FilesPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        label(self, "FILE SECURITY", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        cols = tk.Frame(self, bg=T["bg_dark"])
        cols.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)
        left = tk.Frame(cols, bg=T["bg_dark"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = tk.Frame(cols, bg=T["bg_dark"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- hash auditor
        hp = panel(left, "FILE HASH AUDITOR (SHA-256)", T["accent_lime"])
        hp.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        button(hp, "SELECT FILE & SCAN", self.scan_file, T["accent_lime"]).pack(pady=6)
        self.hash_out = text_box(hp, T["accent_lime"], height=7)
        set_text(self.hash_out, "Pick any file. Known-bad hashes trigger quarantine.\n"
                                "Demo: save a text file containing exactly CYBERSHIELD-TEST-FILE and scan it.")

        # --- PE analyzer
        pp = panel(left, "PE EXECUTABLE ANALYZER (static, never runs the file)", T["accent_orange"])
        pp.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        button(pp, "SELECT .EXE / .DLL", self.analyze_pe, T["accent_orange"]).pack(pady=6)
        self.pe_out = text_box(pp, T["accent_orange"], height=7)

        # --- folder integrity
        ip = panel(right, "FOLDER INTEGRITY MONITOR", T["accent_cyan"])
        ip.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.folder = tk.StringVar(value="")
        tk.Label(ip, textvariable=self.folder, fg=T["text_muted"], bg=T["bg_dark"], font=("Consolas", 8),
                 wraplength=380, justify=tk.LEFT).pack(anchor="w", padx=8, pady=(6, 0))
        row = tk.Frame(ip, bg=T["bg_dark"])
        row.pack(pady=6)
        button(row, "CHOOSE FOLDER", self.choose_folder).pack(side=tk.LEFT, padx=3)
        button(row, "CREATE BASELINE", self.create_baseline, T["accent_lime"]).pack(side=tk.LEFT, padx=3)
        button(row, "SCAN FOR CHANGES", self.scan_folder, T["accent_magenta"]).pack(side=tk.LEFT, padx=3)
        self.int_out = text_box(ip, T["accent_cyan"], height=16)
        set_text(self.int_out, "1) Choose a folder  2) Create baseline  3) Later, scan.\n"
                               "Modified, new and deleted files are reported.")

    # ----- hash auditor
    def scan_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        set_text(self.hash_out, "Scanning...")
        run_async(self, lambda: file_tools.scan_file(path), lambda ok, res: self._scan_done(path, ok, res))

    def _scan_done(self, path, ok, res):
        if not ok:
            set_text(self.hash_out, f"Error: {res}")
            return
        lines = [f"File   : {path}", f"Size   : {res['size']} bytes", f"SHA-256: {res['sha256']}", ""]
        if res["threat"]:
            lines.append(f"VERDICT: KNOWN THREAT -> {res['threat']}")
            set_text(self.hash_out, "\n".join(lines))
            if messagebox.askyesno("Threat found", "Quarantine this file?\nIt will be encrypted into the vault "
                                   "and the original securely deleted."):
                ok2, msg = file_tools.quarantine_file(path, res["threat"])
                (messagebox.showinfo if ok2 else messagebox.showwarning)("Quarantine", msg)
        else:
            lines.append("VERDICT: no known signature match.")
            set_text(self.hash_out, "\n".join(lines))

    # ----- PE analyzer
    def analyze_pe(self):
        if not pe_analyzer.HAS_PEFILE:
            set_text(self.pe_out, "pefile is not installed.\nRun: pip install pefile")
            return
        path = filedialog.askopenfilename(filetypes=[("Executables", "*.exe *.dll *.sys"), ("All files", "*.*")])
        if path:
            set_text(self.pe_out, "Analyzing...")
            run_async(self, lambda: pe_analyzer.analyze_pe(path), self._pe_done)

    def _pe_done(self, ok, res):
        if not ok:
            set_text(self.pe_out, f"Could not parse file: {res}")
            return
        lines = [f"Machine : {res['machine']}", f"Compiled: {res['compiled']}", "", "SECTIONS (name, size, entropy)"]
        for s in res["sections"]:
            flag = "  <-- high entropy, possibly packed" if s["packed"] else ""
            lines.append(f" {s['name']:<8} {hex(s['virtual_size']):<10} {s['entropy']}{flag}")
        lines += ["", f"IMPORTED DLLs ({len(res['imports'])}): " + ", ".join(res["imports"][:12])]
        set_text(self.pe_out, "\n".join(lines))

    # ----- folder integrity
    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder.set(path)

    def _need_folder(self):
        if not self.folder.get():
            messagebox.showinfo("Folder needed", "Choose a folder first.")
            return None
        return self.folder.get()

    def create_baseline(self):
        folder = self._need_folder()
        if folder:
            set_text(self.int_out, "Hashing files...")
            run_async(self, lambda: integrity.create_baseline(folder), self._baseline_done)

    def _baseline_done(self, ok, res):
        set_text(self.int_out, f"Baseline saved for {res} files." if ok else f"Error: {res}")

    def scan_folder(self):
        folder = self._need_folder()
        if folder:
            set_text(self.int_out, "Scanning...")
            run_async(self, lambda: integrity.scan(folder), self._scan_folder_done)

    def _scan_folder_done(self, ok, res):
        if not ok:
            set_text(self.int_out, f"{res}")
            return
        lines = [f"Unchanged: {res['unchanged']}", f"Modified : {len(res['modified'])}",
                 f"New      : {len(res['new'])}", f"Deleted  : {len(res['deleted'])}", ""]
        for title, key in (("MODIFIED", "modified"), ("NEW", "new"), ("DELETED", "deleted")):
            for rel in res[key][:50]:
                lines.append(f"[{title}] {rel}")
        if not (res["modified"] or res["new"] or res["deleted"]):
            lines.append("All files match the baseline.")
        set_text(self.int_out, "\n".join(lines))
