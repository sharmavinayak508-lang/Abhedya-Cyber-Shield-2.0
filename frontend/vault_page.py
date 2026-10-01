"""Vault & traps: master-password vault, quarantine list, honeytoken, RSA demo."""
import tkinter as tk
from tkinter import filedialog, messagebox

from backend import crypto, file_tools, rsa_demo
from backend.honeytoken import sentinel
from backend.logger import log_event
from config import THEME as T
from frontend.base_page import Page
from frontend.widgets import button, entry, label, panel, set_text, table, text_box


class VaultPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.keys = None
        label(self, "VAULT & DECEPTION TRAPS", T["accent_cyan"], 14, True).pack(pady=(12, 4))
        cols = tk.Frame(self, bg=T["bg_dark"])
        cols.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)
        left = tk.Frame(cols, bg=T["bg_dark"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = tk.Frame(cols, bg=T["bg_dark"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- vault
        vp = panel(left, "ENCRYPTED VAULT (master password)", T["accent_cyan"])
        vp.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.status = label(vp, "", T["text_muted"], 11, True)
        self.status.pack(pady=(8, 2))
        self.pw = entry(vp, show="*", width=28)
        self.pw.pack(pady=4)
        self.pw.bind("<Return>", lambda _e: self.on_main())
        row = tk.Frame(vp, bg=T["bg_dark"])
        row.pack(pady=4)
        self.main_btn = button(row, "UNLOCK", self.on_main)
        self.main_btn.pack(side=tk.LEFT, padx=3)
        button(row, "LOCK", self.on_lock, T["accent_orange"]).pack(side=tk.LEFT, padx=3)
        button(row, "RESTORE SELECTED", self.on_restore, T["accent_lime"]).pack(side=tk.LEFT, padx=3)
        self.q_tree = table(vp, [("name", "QUARANTINED FILE", 260), ("size", "BYTES", 70), ("when", "DATE", 120)])

        # --- honeytoken
        hp = panel(right, "HONEYTOKEN (decoy file trap)", T["accent_magenta"])
        hp.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        label(hp, "A fake credentials file nobody should touch.\nAny change fires a CRITICAL alert.",
              T["text_main"], 8, justify=tk.LEFT).pack(pady=6)
        row = tk.Frame(hp, bg=T["bg_dark"])
        row.pack()
        button(row, "DEPLOY TRAP", self.deploy, T["accent_magenta"]).pack(side=tk.LEFT, padx=3)
        button(row, "SIMULATE TAMPERING", self.tamper, T["accent_orange"]).pack(side=tk.LEFT, padx=3)
        self.trap_out = text_box(hp, T["accent_magenta"], height=5)
        set_text(self.trap_out, "Trap not deployed.")

        # --- RSA demo
        rp = panel(right, "RSA DEMO (small primes: for learning only)", T["accent_lime"])
        rp.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        button(rp, "GENERATE KEYS", self.gen_keys, T["accent_lime"]).pack(pady=6)
        self.msg = entry(rp, width=34)
        self.msg.insert(0, "Hello CyberShield")
        self.msg.pack()
        button(rp, "ENCRYPT + DECRYPT MESSAGE", self.demo_roundtrip).pack(pady=6)
        self.rsa_out = text_box(rp, T["accent_lime"], height=8)
        set_text(self.rsa_out, "Click GENERATE KEYS.")

        self.refresh_state()

    def on_show(self):
        self.refresh_state()

    # ----- vault
    def refresh_state(self):
        if not crypto.HAS_CRYPTO:
            self.status.config(text="'cryptography' NOT INSTALLED", fg=T["accent_magenta"])
            return
        if not crypto.vault_exists():
            self.status.config(text="NO VAULT YET", fg=T["accent_orange"])
            self.main_btn.config(text="CREATE VAULT")
        elif crypto.is_unlocked():
            self.status.config(text="UNLOCKED", fg=T["accent_lime"])
            self.main_btn.config(text="UNLOCK")
        else:
            self.status.config(text="LOCKED", fg=T["accent_magenta"])
            self.main_btn.config(text="UNLOCK")
        self.q_tree.delete(*self.q_tree.get_children())
        for name, size, when in file_tools.list_quarantined():
            self.q_tree.insert("", tk.END, values=(name, size, when))

    def on_main(self):
        password = self.pw.get()
        self.pw.delete(0, tk.END)
        if not crypto.HAS_CRYPTO:
            messagebox.showerror("Missing package", "Install it with: pip install cryptography")
            return
        if not crypto.vault_exists():
            try:
                crypto.setup_vault(password)
                log_event("Vault created and unlocked.", "INFO")
            except ValueError as exc:
                messagebox.showwarning("Weak password", str(exc))
        elif crypto.unlock_vault(password):
            log_event("Vault unlocked.", "INFO")
        else:
            log_event("Wrong vault master password entered.", "WARN")
            messagebox.showerror("Denied", "Wrong master password.")
        self.refresh_state()

    def on_lock(self):
        crypto.lock_vault()
        log_event("Vault locked.", "INFO")
        self.refresh_state()

    def on_restore(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showinfo("Select a file", "Click a quarantined file first.")
            return
        dest = filedialog.askdirectory(title="Restore into which folder?")
        if dest:
            ok, msg = file_tools.restore_file(self.q_tree.item(sel[0], "values")[0], dest)
            (messagebox.showinfo if ok else messagebox.showwarning)("Restore", msg)

    # ----- honeytoken
    def deploy(self):
        try:
            path = sentinel.deploy()
            set_text(self.trap_out, f"ARMED. Watching:\n{path}")
        except OSError as exc:
            messagebox.showerror("Error", str(exc))

    def tamper(self):
        if not sentinel.active:
            messagebox.showinfo("Deploy first", "Deploy the trap before simulating tampering.")
            return
        sentinel.simulate_tamper()
        set_text(self.trap_out, "Decoy modified. Watch the log feed for a CRITICAL alert (within ~1 second).")

    # ----- RSA
    def gen_keys(self):
        self.keys = rsa_demo.generate_keys()
        k = self.keys
        set_text(self.rsa_out, f"p={k['p']}  q={k['q']}\nn={k['n']}  phi={k['phi']}\n"
                               f"PUBLIC  (e, n) = ({k['e']}, {k['n']})\nPRIVATE (d, n) = ({k['d']}, {k['n']})")

    def demo_roundtrip(self):
        if not self.keys:
            self.gen_keys()
        k = self.keys
        text = self.msg.get()
        cipher = rsa_demo.encrypt_text(text, k["e"], k["n"])
        plain = rsa_demo.decrypt_text(cipher, k["d"], k["n"])
        set_text(self.rsa_out, f"Plain  : {text}\nCipher : {cipher}\nDecrypt: {plain}")
