import os
import sys

# Determine where the EXE or Script is running from
if getattr(sys, 'frozen', False):
    APP_ROOT = os.path.dirname(sys.executable)
    BASE_PATH = sys._MEIPASS # Where PyInstaller unpacks temp files
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    BASE_PATH = APP_ROOT

# Define Absolute Paths
RECEIPTS_DIR = os.path.join(APP_ROOT, 'Receipts')
REPORTS_DIR = os.path.join(APP_ROOT, 'Reports')
DATA_DIR = os.path.join(APP_ROOT, 'Data')
ASSETS_DIR = os.path.join(BASE_PATH, 'assets')

# This puts 3DP_Database.db INSIDE the Data folder
DB_PATH = os.path.join(DATA_DIR, '3DP_Database.db')
LOGO_PATH = os.path.join(ASSETS_DIR, 'Logo.png')
SETTINGS_ICON = os.path.join(ASSETS_DIR, 'settings_icon.png')

# Create folders immediately
try:
    for folder in [RECEIPTS_DIR, REPORTS_DIR, DATA_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
except OSError as e:
    # No Tk root exists yet this early, so spin up a throwaway one just for the dialog
    import tkinter as tk
    from tkinter import messagebox
    _root = tk.Tk()
    _root.withdraw()
    messagebox.showerror("Fatal Error", f"Could not create required folders:\n{e}")
    _root.destroy()
    sys.exit(1)