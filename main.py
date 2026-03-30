# Call required libraries
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime

# Import Custom Modules
import database
import logic
import export

# Define Global Themes for Light and Dark Mode
THEMES = {
    "light": {
        "bg": "#F8F9FA",       # Penelope Off-white
        "card": "#FFFFFF",     # Pure white
        "text": "#2C3E50",     # Dark Navy
        "accent": "#FF9F43",   # Penelope Orange
        "secondary": "#5758BB", # Penelope Indigo
        "entry_bg": "#F1F2F6"
    },
    "dark": {
        "bg": "#1E272E",       # Hazenthley Deep Navy
        "card": "#2D3436",     # Hazenthley Charcoal
        "text": "#FFFFFF",     # White
        "accent": "#F1C40F",   # Hazenthley Yellow
        "secondary": "#0984E3", # Hazenthley Cyan
        "entry_bg": "#34495E"
    }
}

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3DP Cost Calculator")
        self.root.geometry("400x500")
        
        # Default Theme
        self.current_theme = "light" 
        self.theme_elements = []
        
        # Initialize Database on startup
        database.initialize_database()
        
        self.create_toolbar()
        self.create_main()
        
        # Window Icon Setup
        try:
            # Load the image using Pillow
            icon_path = "assets/Logo.png" 
            icon_img = Image.open(icon_path)
            self.app_icon = ImageTk.PhotoImage(icon_img)
            
            # Set the icon (True makes it apply to all popup windows too)
            self.root.iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"Window icon failed to load: {e}")
            
        # Apply Default Theme
        self.apply_theme()
            
    def toggle_theme(self):
        """Switches the theme and triggers a UI repaint"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        
    def apply_theme(self):
        """Universal Paintbrush: Purple Toolbar | Black-to-Yellow Calculate Button"""
        colors = THEMES[self.current_theme]
        
        # 1. Main Background and Card
        self.root.configure(bg=colors["bg"])
        self.content_frame.configure(bg=colors["card"])
        
        # 2. TOOLBAR: Always Penelope Indigo (#5758BB)
        toolbar_color = colors["secondary"] 
        self.toolbar.configure(bg=toolbar_color)

        # 3. Handle Icons and Logo backgrounds to match the purple toolbar
        if hasattr(self, 'theme_btn'):
            new_icon = "☀️" if self.current_theme == "dark" else "🌙"
            self.theme_btn.configure(text=new_icon, bg=toolbar_color, fg="white")
            
        if hasattr(self, 'settings_btn'):
            self.settings_btn.configure(bg=toolbar_color, activebackground=toolbar_color)
            
        if hasattr(self, 'logo_label'):
            self.logo_label.configure(bg=toolbar_color)

        # 4. Loop through registered elements
        for element in self.theme_elements:
            try:
                if element.winfo_exists():
                    # If it's in the toolbar, match the purple
                    if element.master == self.toolbar:
                        element.configure(bg=toolbar_color, fg="white")
                    else:
                        # Otherwise, match the main card/bg colors
                        element.configure(bg=colors["card"], fg=colors["text"])
                    
                    # 5. SPECIAL CASE: CALCULATE BUTTON COLOR SWAP
                    if isinstance(element, tk.Button) and "Calculate" in element.cget("text"):
                        if self.current_theme == "dark":
                            # HAZENTHLEY YELLOW: Yellow background, Black text
                            element.configure(
                                bg=colors["accent"],  # #F1C40F
                                fg="black", 
                                activebackground="#D4AC0D" # Slightly darker yellow for hover
                            )
                        else:
                            # PENELOPE BLACK/NAVY: Dark background, White text
                            element.configure(
                                bg="#2C3E50", 
                                fg="white", 
                                activebackground="#34495E"
                            )
            except:
                continue
        
    # Load Last Job Data into Input Fields for Quick Reprint
    def load_last_job(self):
        last = database.get_last_receipt()
        if last:
            mat_name, weight, hours = last
            self.mat_combo.set(mat_name)
            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(weight))
            self.hours_entry.delete(0, tk.END)
            self.hours_entry.insert(0, str(hours))
            messagebox.showinfo("Loaded", "Last job data filled.")
        else:
            messagebox.showwarning("Empty", "No previous orders found.")
            
    def generate_report(self):
        from datetime import datetime
        # Get current month and year automatically
        now = datetime.now()
        m = now.strftime('%m') 
        y = now.strftime('%Y')
        
        data = database.get_monthly_records(m, y)
        
        if not data:
            messagebox.showwarning("No Data", f"No orders found for {m}/{y}.")
            return
        
        filepath = export.export_to_excel(m, y, data)
        
        messagebox.showinfo("Report Exported", f"Monthly report saved successfully!\nLocation: {'Reports'}")
        
    def create_toolbar(self):
        """Creates top icon toolbar for quick access to settings and receipt history"""
        colors = THEMES[self.current_theme]
        self.toolbar = tk.Frame(self.root, bg=colors["bg"], height=60)
        self.toolbar.pack(side="top", fill="x")
        
        # --- LEFT SIDE: Logo & Title ---
        try:
            logo_raw = Image.open("assets/Logo.png").resize((30, 30), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo_raw)
            self.logo_label = tk.Label(self.toolbar, image=self.logo_img, bg=colors['bg'])
            self.logo_label.pack(side="left", padx=(15, 5), pady=10)
            self.theme_elements.append(self.logo_label)
        except: pass

        self.title_lbl = tk.Label(self.toolbar, text="3DP", font=("Arial", 12, "bold"))
        self.title_lbl.pack(side="left", padx=5)
        self.theme_elements.append(self.title_lbl)

        # --- RIGHT SIDE (Packed in order of priority) ---

        # 1. SETTINGS BUTTON (Packed first = Far Right)
        try: 
            settings_raw = Image.open("Assets/settings_icon.png").resize((25,25), Image.Resampling.LANCZOS)
            self.settings_img = ImageTk.PhotoImage(settings_raw)
            self.settings_btn = tk.Button(
                self.toolbar, image=self.settings_img, command=self.open_settings,
                relief="flat", bg=colors['bg'], activebackground=colors['bg'],
                cursor="hand2", bd=0
            )
            self.settings_btn.pack(side="right", padx=(5, 15), pady=10) # Added right-side padding
            self.theme_elements.append(self.settings_btn)
        except: pass

        # 2. TOGGLE BUTTON (Packed second = To the left of Settings)
        self.theme_btn = tk.Button(
            self.toolbar, text="🌙", command=self.toggle_theme,
            relief="flat", bg=colors["bg"], fg=colors["text"], 
            font=("Arial", 12), bd=0, cursor="hand2"
        )
        self.theme_btn.pack(side="right", padx=5)
        self.theme_elements.append(self.theme_btn)
        ttk.Separator(self.root, orient='horizontal').pack(side="top", fill="x")
        
    def create_main(self):
        """"Creates the Main UI for Material Selection, Weight and Hours Input, and Calculate Button"""
        colors = THEMES[self.current_theme]
        self.content_frame = tk.Frame(self.root, bg=colors["card"], padx=40, pady=30)
        self.content_frame.pack(expand=True, fill="both")
        
        def add_lbl(text, font=("Arial", 10), pady=0, is_header=False):
            f = ("Arial", 16, "bold") if is_header else font
            lbl = tk.Label(
                self.content_frame, text=text, font=f, 
                bg=colors["card"], fg=colors["text"])
            lbl.pack(anchor="w", pady=pady)
            self.theme_elements.append(lbl) # Register
            return lbl
        
        add_lbl("Job Details", pady=(0, 20), is_header=True)
        
        mat_lbl = tk.Label(
            self.content_frame, text="Select Material:", 
            bg=colors["card"], fg=colors["text"])
        mat_lbl.pack(anchor="w")
        self.theme_elements.append(mat_lbl)

        # The Combobox Fix
        self.materials = database.get_all_materials()
        self.mat_names = [m[0] for m in self.materials]
        
        self.mat_combo = ttk.Combobox(self.content_frame, values=self.mat_names, state="readonly")
        self.mat_combo.pack(fill="x", pady=(5, 20))
        # Important: Select the first item so it's not 'empty'
        if self.mat_names:
            self.mat_combo.current(0)
        
        add_lbl("Enter Weight (grams):")
        self.weight_entry = ttk.Entry(self.content_frame)
        self.weight_entry.pack(fill="x", pady=(5, 20))
        
        add_lbl("Enter Print Time (hours):")
        self.hours_entry = ttk.Entry(self.content_frame)
        self.hours_entry.pack(fill="x", pady=(5, 20))
        
        # Calculate Button - Always keeps its text white but changes BG color
        self.calc_btn = tk.Button(
            self.content_frame, text=" Calculate Cost ", command=self.calculate_cost,
            bg=colors["accent"], fg="white", font=("Arial", 11, "bold"),
            relief="flat", height=2, cursor="hand2" 
        )
        self.calc_btn.pack(fill="x", pady=(0, 10))
        self.theme_elements.append(self.calc_btn) # Register
        
        load_btn = tk.Button(
            self.content_frame, text="🔄 Load Last Job for Reprint", command=self.load_last_job,
            bg=colors["accent"], fg=colors["text"], font=("Arial", 10),
            relief="flat", height=1, cursor="hand2" 
        )
        load_btn.pack(fill="x")
    
    # Refresh Materials List in Dropdown after Adding new Material
    def refresh_materials(self):
        """Reloads materials from DB and updates the dropdown menu"""
        self.materials = database.get_all_materials()
        self.mat_names = [m[0] for m in self.materials]
        self.mat_combo['values'] = self.mat_names
        # Optional: Select the newest material automatically
        if self.mat_names:
            self.mat_combo.set(self.mat_names[-1])
    
    # Logic Implementation for Cost Calculation
    def calculate_cost(self):
        """Calculates the total cost of a 3D print job based on user input and database values"""
        try:
            name = self.mat_combo.get()
            w = float(self.weight_entry.get())
            h = float(self.hours_entry.get())
            
            if not name:
                messagebox.showwarning("Incomplete", "Please select a material.")
                return
            if w <= 0  or h <= 0:
                messagebox.showwarning("Invalid Input", "Please Enter Valid Weight and Hours.")
                return
            
            # Retrieve Material Data and Global Settings from Database
            mat_data = next((m for m in self.materials if m[0] == name), None)
            settings = database.get_settings()
            
            order_id = database.get_next_order_id()
            
            # Calculate Total Cost using Logic Module
            total_cost, rate_label = logic.calculate_cost(w, h, mat_data, settings)
            
            # Open Preview Window 
            self.show_preview(name, w, h, rate_label, total_cost, order_id)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for weight and hours.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Something went wrong: {e}")
    
    # Function to Show Cost Breakdown and Receipt Generation Option
    def show_preview(self, mat, w, h, rate_label, total_cost, order_id):
        """Top Level Function to Show Cost Breakdown and Receipt Generation Option"""
        preview = tk.Toplevel(self.root)
        preview.title(f"Cost Breakdown - Order # {order_id}")
        preview.geometry("400x520")
        preview.configure(padx=30, pady=20)
        
        # Receipt Format
        header = f"3d Print Job Cost Breakdown \n---------------------------- \nDate: {datetime.now().strftime('%Y-%m-%d')}"
        body = f"\nMaterial: {mat} \nWeight: {w:.0f}g \nPrint Time: {h:.2f} hrs \n\nRate: {rate_label}\n"
        footer = f"\n----------------------------\n TOTAL: Php {total_cost:.2f} \n----------------------------\n Thank you!"
        
        tk.Label(preview, text=header + body + footer, font=("Courier", 12), justify="left").pack(pady=20)
        
        # Unique FileName for Receipt Export
        f_base = f"Receipt_Order_{order_id}_{mat}"
        
        # Export Logic
        def handle_export(export_type):
            """Internal helper to manage file generation and DB Logging"""
            try:
                # Set extension and full filename based on export type
                ext= ".pdf" if export_type == "PDF" else ".png"
                filename_full = f_base + ext
                
                # Call Export Module to Generate File
                if export_type == "PDF":
                    export.generate_pdf(f_base, mat, w, h, rate_label, total_cost)
                else: 
                    export.generate_png(f_base, mat, w, h, rate_label, total_cost)
                    
                # Save Receipt Data to Database
                data = f"Tier: {rate_label}"
                database.save_receipt(data, filename_full, mat, w, h, total_cost)
                
                messagebox.showinfo("Export Successful", f"Order #{order_id} exported as {export_type}")
                preview.destroy() # Close Preview after Export
                
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export {export_type}: {e}")
                
        # Export Buttons
        btn_container = tk.Frame(preview)
        btn_container.pack(pady=10)
        
        # PDF Export Button
        pdf_btn = tk.Button(
            btn_container, text="📄 Export as PDF",
            command=lambda: handle_export("PDF"),
            bg="#2c3e50", fg="white", font=("Arial", 10, "bold"),
            width=20, pady=8, cursor="hand2", relief="flat"
        )
        pdf_btn.pack(pady=5)
        
        # PNG Export Button
        img_btn = tk.Button(
            btn_container, text="🖼️ Save as Image", 
            command=lambda: handle_export("Image"),
            bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
            width=20, pady=8, cursor="hand2", relief="flat"
        )        
        img_btn.pack(pady=5)
    
    def open_settings(self):
        """Creates a Settings Window to Update Meralco Rate and Setup Fee"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x650")
        settings_win.configure(padx=20, pady=20)
        
        # Fetch Current Settings from Database
        current_settings = database.get_settings()
        # current setting is (Meralco Rate, Setup Fee)
        
        tk.Label(settings_win, text="Update Settings", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Meralco Rate Input
        tk.Label(settings_win, text="Meralco Rate (Php/kWh):").pack(anchor="w")
        rate_entry = ttk.Entry(settings_win, font=("Arial", 10))
        rate_entry.insert(0, str(current_settings[0]))
        rate_entry.pack(fill="x", pady=(5, 15))
        
        # Setup Fee Input
        tk.Label(settings_win, text="Setup Fee (Php):").pack(anchor="w")
        fee_entry = ttk.Entry(settings_win, font=("Arial", 10))
        fee_entry.insert(0, str(current_settings[1]))
        fee_entry.pack(fill="x", pady=(5, 25))
        
        # Material Management Button
        ttk.Separator(settings_win, orient='horizontal').pack(fill="x", pady=20)
        tk.Label(settings_win, text="Add New Material", font=("Arial", 12, "bold")).pack(anchor="w")
        
        tk.Label(settings_win, text="Material Name:").pack(anchor="w")
        new_mat_name = ttk.Entry(settings_win)
        new_mat_name.pack(fill="x")

        tk.Label(settings_win, text="Wattage (W):").pack(anchor="w")
        new_mat_watt = ttk.Entry(settings_win)
        new_mat_watt.pack(fill="x")

        tk.Label(settings_win, text="Price per Gram (Php):").pack(anchor="w")
        new_mat_price = ttk.Entry(settings_win)
        new_mat_price.pack(fill="x")

        def add_mat_logic():
            try:
                n = new_mat_name.get()
                w = float(new_mat_watt.get())
                p = float(new_mat_price.get())
                if n:
                    database.add_material(n, w, p)
                    messagebox.showinfo("Success", f"{n} added!")
                    self.refresh_materials() # Update the main dropdown
                    settings_win.destroy()
            except:
                messagebox.showerror("Error", "Invalid Material Data")

        tk.Button(settings_win, text="+ Add Material", command=add_mat_logic, 
            bg="#27ae60", fg="white", relief="flat").pack(fill="x", pady=10)
        
        ttk.Separator(settings_win, orient='horizontal').pack(fill="x", pady=20)
        tk.Label(settings_win, text="Business Reports", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Report Generation Logic
        def run_report_logic():
            # Get current Month and Year
            from datetime import datetime
            now = datetime.now()
            m = now.strftime('%m')
            y = now.strftime('%Y')

            # Fetch data from DB
            report_data = database.get_monthly_records(m, y)
            
            if not report_data:
                messagebox.showwarning("No Data", f"No orders found for {m}/{y}.")
                return

            # Trigger the Excel/CSV export from export.py
            filepath = export.export_to_excel(m, y, report_data)
            messagebox.showinfo("Success", f"Monthly Report Exported!\nLocation: {filepath}")

        # The Export Button (Blue color to distinguish it from "Add" or "Save")
        report_btn = tk.Button(
            settings_win, text="📊 Export Monthly Report (Excel)", 
            command=run_report_logic,
            bg="#3498db", fg="white", font=("Arial", 10, "bold"),
            height=2, relief="flat", cursor="hand2"
        )
        report_btn.pack(fill="x", pady=10)
        
        # Save Logic
        def save_new_settings():
            try:
                # Get new values from entries
                new_rate = float(rate_entry.get())
                new_fee = float(fee_entry.get())
                
                # Validation for positive numbers
                if new_rate <= 0 or new_fee < 0:
                    messagebox.showwarning("Invalid Input", "Please enter valid positive numbers.")
                    return
                
                # Update Settings in Database
                database.update_settings(new_rate, new_fee)
                
                # Confirmation Message
                messagebox.showinfo("Settings Updated", "Rates have been updated successfully!")
                settings_win.destroy()
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for rates.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            
        # Save Button
        save_btn = tk.Button(
            settings_win, text="Save Settings", command=save_new_settings,
            bg="#2980b9", fg="white", font=("Arial", 11, "bold"),
            relief="flat", width=20, pady=8, cursor="hand2" 
        )
        save_btn.pack(fill="x")

# Start Application
if __name__ == "__main__":
    root = tk.Tk()
    
    style = ttk.Style(root)
    style.theme_use("clam")
    
    app = CalculatorApp(root)
    
    root.mainloop()