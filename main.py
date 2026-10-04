"""CyberShield entry point:  python main.py"""
import tkinter as tk

from backend import auth, database, portal_client
from config import APP_NAME, THEME
from frontend.dashboard import Dashboard
from frontend.login import LoginFrame


def main():
    database.init_database()
    auth.ensure_default_user()
    portal_client.start()  # optional: does nothing unless data/portal.json exists

    root = tk.Tk()
    root.title(APP_NAME)
    root.configure(bg=THEME["bg_dark"])

    def show_login():
        LoginFrame(root, on_success=show_dashboard)

    def show_dashboard(username):
        Dashboard(root, username, on_logout=show_login)

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
