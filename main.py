# Call required libraries
import tkinter as tk
import sys
import os
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Import Custom Modules
import database
import logic
import report_handler
from material_manager import MaterialManagerWindow
from config import LOGO_PATH, SETTINGS_ICON 
from settings import SettingsWindow
from preview import PreviewWindow

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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

logo_raw = Image.open(resource_path(LOGO_PATH)).resize((40, 40), Image.Resampling.LANCZOS)
settings_raw = Image.open(resource_path(SETTINGS_ICON)).resize((25,25), Image.Resampling.LANCZOS)

# Class Definition for Main Application
class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3DP Cost Calculator")
        self.root.geometry("400x500")
        
        # Default Theme
        self.current_theme = "light" 
        self.theme_elements = []
        
        # Initialize Database on startup
        try:
            database.initialize_database()
        except RuntimeError as e:
            messagebox.showerror("Fatal Error", f"Could not start application:\n{e}")
            sys.exit(1)

        self.create_toolbar()
        self.create_main()
        
        # Window Icon Setup
        try:
            # Use the absolute path from config.py
            from config import LOGO_PATH
            from PIL import Image, ImageTk
            
            # Load and convert for Tkinter
            icon_img = Image.open(LOGO_PATH)
            self.app_icon = ImageTk.PhotoImage(icon_img)
            
            # Set the icon for the main window and all future Toplevels (True)
            self.root.iconphoto(True, self.app_icon)
            
        except Exception as e:
            # This will catch if the file is missing or path is wrong
            print(f"Window icon failed to load from {LOGO_PATH}: {e}")
            
        # Apply Default Theme
        self.apply_theme()
            
    def toggle_theme(self):
        """Switches the theme and triggers a UI repaint"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        
    def get_theme_colors(self):
        """Helper for external files to fetch current palette"""
        return THEMES[self.current_theme]
    
    def apply_theme(self):
        colors = THEMES[self.current_theme]
        
        # 1. Clean list and handle static containers immediately
        self.theme_elements = [el for el in self.theme_elements if el.winfo_exists()]
        
        # Define a quick map for clarity
        is_dark = self.current_theme == "dark"
        accent_bg = colors["accent"] if is_dark else "#2C3E50"
        accent_fg = "black" if is_dark else "white"
        
        # Backgrounds that always behave the same
        self.root.configure(bg=colors["bg"])
        self.toolbar.configure(bg=colors["secondary"])
        self.content_frame.configure(bg=colors["card"])
        # Time input row sits on the card, so it follows the card color
        if hasattr(self, 'time_frame'):
            self.time_frame.configure(bg=colors["card"])

        # Update Theme Toggle Icon specifically
        if hasattr(self, 'theme_btn'):
            self.theme_btn.configure(text="☀️" if is_dark else "🌙")

        # 2. THE UNIVERSAL LOOP (One pass for everything)
        for el in self.theme_elements:
            try:
                # --- WINDOWS / FRAMES ---
                if isinstance(el, (tk.Toplevel, tk.Frame)):
                    # If it's a breakdown window/frame, use card color, else standard bg
                    title = el.winfo_toplevel().title()
                    bg = colors["card"] if "Breakdown" in title else colors["bg"]
                    el.configure(bg=bg)

                # --- LABELS ---
                elif isinstance(el, tk.Label):
                    # Inherit from parent floor
                    p_bg = el.master.cget("bg")
                    el.configure(bg=p_bg, fg=colors["text"])

                # --- BUTTONS ---
                elif isinstance(el, tk.Button):
                    txt = el.cget("text").lower()
                    
                    # Logic Switchboard
                    if any(k in txt for k in ["calculate", "save", "load"]):
                        el.configure(bg=accent_bg, fg=accent_fg)
                    elif any(k in txt for k in ["export", "report"]) or el.master == self.toolbar:
                        el.configure(bg=colors["secondary"], fg="white")
                    elif "add" in txt:
                        el.configure(bg="#27ae60", fg="white")
                    
                    # Global button cleanup (removes ugly hover borders)
                    el.configure(activebackground=el.cget("bg"))
                    
                elif isinstance(el, tk.Entry):
                    # In Dark Mode: Dark grey background with white text
                    # In Light Mode: White background with black text
                    bg = "#2f3640" if self.current_theme == "dark" else "white"
                    fg = "white" if self.current_theme == "dark" else "black"
                    el.configure(bg=bg, fg=fg, insertbackground=fg) # insertbackground is the cursor color

            except Exception:
                continue
            
    def generate_report(self):
        report_handler.generate_monthly_report()
        
    def create_toolbar(self):
        """Creates top icon toolbar for quick access to settings and receipt history"""
        colors = THEMES[self.current_theme]
        self.toolbar = tk.Frame(self.root, bg=colors["bg"], height=60)
        self.toolbar.pack(side="top", fill="x")
        
        # --- LEFT SIDE: Logo & Title ---
        try:
            # Wrap path in resource_path()
            logo_path = resource_path("Assets/Logo.png")
            logo_raw = Image.open(logo_path).resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo_raw)
            self.logo_label = tk.Label(self.toolbar, image=self.logo_img, bg=colors['bg'])
            self.logo_label.pack(side="left", padx=(15, 5), pady=10)
            self.theme_elements.append(self.logo_label)
        except: pass

        self.title_lbl = tk.Label(self.toolbar, text="3DP", font=("Arial", 12, "bold"))
        self.title_lbl.pack(side="left", padx=5)
        self.theme_elements.append(self.title_lbl)

        # --- RIGHT SIDE (Packed in order of priority) ---
        
        # 1. SETTINGS BUTTON (Packed Far Right)
        try: 
            settings_path = resource_path("Assets/settings_icon.png")
            settings_raw = Image.open(settings_path).resize((25,25), Image.Resampling.LANCZOS)
            self.settings_img = ImageTk.PhotoImage(settings_raw)
            self.settings_btn = tk.Button(
                self.toolbar, image=self.settings_img, command=self.open_settings,
                relief="flat", bg=colors['bg'], activebackground=colors['bg'],
                cursor="hand2", bd=0
            )
            self.settings_btn.pack(side="right", padx=(5, 15), pady=10) 
            self.theme_elements.append(self.settings_btn)
        except Exception as e:
            print(f"Settings Icon Error: {e}")

        # 2. MANAGE MATERIALS BUTTON
        try: 
            mat_path = resource_path("Assets/materials_icon.png")
            mat_raw = Image.open(mat_path).resize((25,25), Image.Resampling.LANCZOS)
            self.mat_img = ImageTk.PhotoImage(mat_raw)
            self.mat_btn = tk.Button(
                self.toolbar, image=self.mat_img, command=self.open_materials_mgr,
                relief="flat", bg=colors['bg'], activebackground=colors['bg'],
                cursor="hand2", bd=0
            )
            self.mat_btn.pack(side="right", padx=5, pady=10) 
            self.theme_elements.append(self.mat_btn)
        except Exception as e: 
            print(f"Materials Icon Error: {e}") 

        # 3. TOGGLE THEME BUTTON
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
        try:
            self.materials = database.get_all_materials()
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            self.materials = []
        self.mat_names = [m[0] for m in self.materials]

        self.mat_combo = ttk.Combobox(self.content_frame, values=self.mat_names, state="readonly")
        self.mat_combo.pack(fill="x", pady=(5, 20))
        # Important: Select the first item so it's not 'empty'
        if self.mat_names:
            self.mat_combo.current(0)
        
        add_lbl("Enter Weight (grams):")
        self.weight_entry = tk.Entry(self.content_frame, relief="flat", font=("Arial", 11))
        self.weight_entry.pack(fill="x", pady=(5, 20))
        self.theme_elements.append(self.weight_entry) # Add to registry!
        
        add_lbl("Enter Print Time (hours & minutes):")
        # Side-by-side hours and minutes inputs
        self.time_frame = tk.Frame(self.content_frame, bg=colors["card"])
        self.time_frame.pack(fill="x", pady=(5, 20))

        self.hours_entry = tk.Entry(self.time_frame, relief="flat", font=("Arial", 11), width=6)
        self.hours_entry.pack(side="left", fill="x", expand=True)
        self.hours_entry.insert(0, "0")
        self.theme_elements.append(self.hours_entry) # Add to registry!

        hrs_lbl = tk.Label(self.time_frame, text="hrs", bg=colors["card"], fg=colors["text"])
        hrs_lbl.pack(side="left", padx=(8, 20))
        self.theme_elements.append(hrs_lbl)

        self.mins_entry = tk.Entry(self.time_frame, relief="flat", font=("Arial", 11), width=6)
        self.mins_entry.pack(side="left", fill="x", expand=True)
        self.mins_entry.insert(0, "0")
        self.theme_elements.append(self.mins_entry) # Add to registry!

        mins_lbl = tk.Label(self.time_frame, text="mins", bg=colors["card"], fg=colors["text"])
        mins_lbl.pack(side="left", padx=(8, 0))
        self.theme_elements.append(mins_lbl)

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
        # CRITICAL: Add this line so the theme loop can find it
        self.theme_elements.append(load_btn)
        
    def refresh_material_dropdown(self):
        """Re-pulls materials from DB and updates the combobox without losing selection."""
        # 1. Capture selection
        current_selection = self.mat_combo.get()

        # 2. Get data (Assuming database is imported at top of file)
        try:
            self.materials = database.get_all_materials()
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.mat_names = [m[0] for m in self.materials]

        # 3. Update UI
        self.mat_combo['values'] = self.mat_names
        
        # 4. Smart Selection
        if current_selection in self.mat_names:
            self.mat_combo.set(current_selection)
        elif self.mat_names:
            self.mat_combo.current(0)
        else:
            self.mat_combo.set('')
    
    # Logic Implementation for Cost Calculation
    def calculate_cost(self):
        """Calculates the total cost of a 3D print job based on user input and database values"""
        try:
            name = self.mat_combo.get()
            w = float(self.weight_entry.get())
            # Blank time fields count as zero so users can enter minutes only
            h = int(self.hours_entry.get().strip() or 0)
            m = int(self.mins_entry.get().strip() or 0)

            if not name:
                messagebox.showwarning("Incomplete", "Please select a material.")
                return
            if h < 0 or m < 0 or m > 59:
                messagebox.showwarning("Invalid Input", "Minutes must be between 0 and 59.")
                return
            if w <= 0  or (h == 0 and m == 0):
                messagebox.showwarning("Invalid Input", "Please Enter Valid Weight and Print Time.")
                return

            # Retrieve Material Data and Global Settings from Database
            mat_data = next((m for m in self.materials if m[0] == name), None)
            if mat_data is None:
                messagebox.showwarning("Invalid Material", "That material no longer exists. Please refresh your selection.")
                return

            settings = database.get_settings()
            order_id = database.get_next_order_id()

            # Calculate Total Cost using Logic Module
            total_cost, rate_label = logic.calculate_cost(w, h, m, mat_data, settings)

            # Open Preview Window
            PreviewWindow(self, name, w, h, m, rate_label, total_cost, order_id)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid weight, and whole numbers for hours and minutes.")
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Something went wrong: {e}")
    
    # Load Last Job Data into Input Fields for Quick Reprint
    def load_last_job(self):
        try:
            last = database.get_last_receipt()
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return
        if last:
            mat_name, weight, hours = last
            # Stored print time is decimal hours, so split it back into hrs + mins
            h, m = logic.split_duration(hours)
            self.mat_combo.set(mat_name)
            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(weight))
            self.hours_entry.delete(0, tk.END)
            self.hours_entry.insert(0, str(h))
            self.mins_entry.delete(0, tk.END)
            self.mins_entry.insert(0, str(m))
            messagebox.showinfo("Loaded", "Last job data filled.")
        else:
            messagebox.showwarning("Empty", "No previous orders found.")
    
    def open_settings(self):
        """Creates a Settings Window to Update Meralco Rate and Setup Fee"""
        try:
            SettingsWindow(self)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))

    def open_materials_mgr(self):
        """Creates a Material Manager Window to Add or Remove Materials from the Database"""
        try:
            MaterialManagerWindow(self)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))

# Start Application
if __name__ == "__main__":
    root = tk.Tk()
    
    style = ttk.Style(root)
    style.theme_use("clam")
    
    app = CalculatorApp(root)
    
    root.mainloop()