import tkinter as tk
from tkinter import ttk, messagebox
import database
import export
from datetime import datetime


class SettingsWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.colors = main_app.get_theme_colors()
        
        # 1. Create the Window 
        self.win = tk.Toplevel(main_app.root)
        self.win.title("Settings")
        self.win.geometry("400x350")
        self.win.configure(bg=self.colors["bg"], padx=20, pady=20)
        
        # 2. Register the window for background flipping
        self.main_app.theme_elements.append(self.win)
        
        # 3. Create widgets and then paint them
        self.create_widgets()
        self.main_app.apply_theme()

    def add_themed_label(self, text, font=("Arial", 10), is_header=False):
        """Helper to create and register labels in one go"""
        f = ("Arial", 14, "bold") if is_header else font
        lbl = tk.Label(self.win, text=text, font=f, bg=self.colors["bg"], fg=self.colors["text"])
        lbl.pack(anchor="w", pady=(10, 2) if not is_header else (0, 15))
        self.main_app.theme_elements.append(lbl)
        return lbl

    def create_widgets(self):
        current_settings = database.get_settings()
        
        self.add_themed_label("Update Settings", is_header=True)
        
        # Rate Inputs
        self.add_themed_label("Meralco Rate (Php/kWh):")
        self.rate_entry = ttk.Entry(self.win)
        self.rate_entry.insert(0, str(current_settings[0]))
        self.rate_entry.pack(fill="x", pady=5)

        self.add_themed_label("Setup Fee (Php):")
        self.fee_entry = ttk.Entry(self.win)
        self.fee_entry.insert(0, str(current_settings[1]))
        self.fee_entry.pack(fill="x", pady=5)

        ttk.Separator(self.win, orient='horizontal').pack(fill="x", pady=20)
        
        # Export Report Button
        self.report_btn = tk.Button(self.win, text="📊 Export Monthly Report", command=self.handle_monthly_report, relief="flat")
        self.report_btn.pack(fill="x", pady=10)
        self.main_app.theme_elements.append(self.report_btn) # REGISTRY

        # Save Button
        self.save_btn = tk.Button(self.win, text="Save All Settings", command=self.save_settings, relief="flat")
        self.save_btn.pack(fill="x", side="bottom", pady=10)
        self.main_app.theme_elements.append(self.save_btn) # REGISTRY

    def save_settings(self):
        try:
            r, f = float(self.rate_entry.get()), float(self.fee_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for Rate and Fee.")
            return

        if r < 0 or f < 0:
            messagebox.showwarning("Invalid Input", "Rate and Fee cannot be negative.")
            return

        try:
            database.update_settings(r, f)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Settings Updated!")
        self.win.destroy()
    
    def handle_monthly_report(self):
        """Helper to bridge the UI, Database, and Export modules"""

        # 1. Get current Month and Year
        now = datetime.now()
        month = now.strftime('%m')
        year = now.strftime('%Y')

        try:
            # 2. Fetch records from DB
            records = database.get_monthly_records(month, year)

            if not records:
                messagebox.showwarning("No Data", f"No records found for {month}/{year}.")
                return

            # 3. Trigger the Export (CSV)
            filename = export.export_to_excel(month, year, records)
            
            messagebox.showinfo("Success", f"Monthly report saved to:\n{filename}")

        except PermissionError:
            messagebox.showerror("Report Error", "Could not save the report — it may be open in another program. Close it and try again.")
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Report Error", f"Could not generate report: {e}")