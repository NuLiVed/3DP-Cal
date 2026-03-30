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
        self.win.geometry("400x700")
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

        self.add_themed_label("Add New Material", is_header=True)
        
        self.add_themed_label("Material Name:")
        self.new_mat_name = tk.Entry(self.win, relief="flat", bg="white")
        self.new_mat_name.pack(fill="x", pady=(0, 10))
        self.main_app.theme_elements.append(self.new_mat_name) # Register for theme

        self.add_themed_label("Wattage (W):")
        self.new_mat_watt = tk.Entry(self.win, relief="flat", bg="white")
        self.new_mat_watt.pack(fill="x", pady=(0, 10))
        self.main_app.theme_elements.append(self.new_mat_watt)

        self.add_themed_label("Price per Gram (Php):")
        self.new_mat_price = tk.Entry(self.win, relief="flat", bg="white")
        self.new_mat_price.pack(fill="x", pady=(0, 10))
        self.main_app.theme_elements.append(self.new_mat_price)

        # Add Material Button
        self.add_btn = tk.Button(
            self.win, 
            text="+ Add Material", 
            command=self.save_material, 
            relief="flat",
            font=("Arial", 10, "bold")
        )
        self.add_btn.pack(fill="x", pady=20)
        self.main_app.theme_elements.append(self.add_btn)
        
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
            database.update_settings(r, f)
            messagebox.showinfo("Success", "Settings Updated!")
            self.win.destroy()
        except:
            messagebox.showerror("Error", "Invalid Rate/Fee Data")

    def save_material(self):
        """
        Handles the full lifecycle of adding a new 3D printing material:
        Validation -> Database Insertion -> UI Refresh -> Cleanup.
        """
        import database
        from tkinter import messagebox
        import sqlite3

        # 1. Capture and Clean Inputs
        # .strip() removes accidental leading/trailing spaces
        name = self.new_mat_name.get().strip()
        watt = self.new_mat_watt.get().strip()
        price = self.new_mat_price.get().strip()

        # 2. Validation: Ensure no fields are empty
        if not name or not watt or not price:
            messagebox.showwarning("Input Error", "All fields (Name, Wattage, Price) are required.")
            return

        try:
            # 3. Data Conversion: Ensure numbers are valid decimals
            watt_val = float(watt)
            price_val = float(price)

            if watt_val <= 0 or price_val <= 0:
                messagebox.showwarning("Input Error", "Wattage and Price must be greater than zero.")
                return
            
            # 4. Database Transaction
            try:
                database.add_material(name, watt_val, price_val)
            except sqlite3.IntegrityError:
                # This triggers if the 'name' already exists in the UNIQUE column
                messagebox.showerror("Duplicate Error", f"Material '{name}' is already in the database.")
                return

            # 5. Success Feedback
            messagebox.showinfo("Success", f"Material '{name}' has been added to the registry.")
            
            # 6. Form Cleanup
            # Clears the entry boxes so the user can add another material immediately
            self.new_mat_name.delete(0, tk.END)
            self.new_mat_watt.delete(0, tk.END)
            self.new_mat_price.delete(0, tk.END)

            # 7. Global UI Synchronization
            # This reaches back to the Main App and updates the dropdown menu
            if hasattr(self.main_app, 'refresh_material_dropdown'):
                self.main_app.refresh_material_dropdown()
            
            # 8. Focus Management (Optional but Pro)
            # Puts the typing cursor back into the Name box for the next entry
            self.new_mat_name.focus_set()

        except ValueError:
            # Triggered if float() fails (e.g., user typed "Ten" instead of "10")
            messagebox.showerror("Format Error", "Wattage and Price must be numeric values (e.g., 120.50).")
        except Exception as e:
            # General catch-all for unexpected system errors
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
    
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
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Could not generate report: {e}")