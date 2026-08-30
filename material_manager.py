import tkinter as tk
from tkinter import ttk, messagebox
import database

class MaterialManagerWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.colors = main_app.get_theme_colors()
        
        # 1. Create the Window 
        self.win = tk.Toplevel(main_app.root)
        self.win.title("Manage Materials")
        self.win.geometry("400x550")
        self.win.configure(bg=self.colors["bg"], padx=20, pady=20)
        
        # 2. Register the window for background flipping
        self.main_app.theme_elements.append(self.win)
        
        # 3. Create widgets and then paint them
        self.create_widgets()
        self.main_app.apply_theme()

    def add_themed_label(self, text, font=("Arial", 10), is_header=False):
        """Helper to create and register labels in one go (Matches your Settings style)"""
        f = ("Arial", 14, "bold") if is_header else font
        lbl = tk.Label(self.win, text=text, font=f, bg=self.colors["bg"], fg=self.colors["text"])
        lbl.pack(anchor="w", pady=(10, 2) if not is_header else (0, 15))
        self.main_app.theme_elements.append(lbl)
        return lbl

    def create_widgets(self):
        # --- ADD MATERIAL SECTION ---
        self.add_themed_label("Add New Material", is_header=True)
        
        self.add_themed_label("Material Name:")
        self.new_mat_name = tk.Entry(self.win, relief="flat")
        self.new_mat_name.pack(fill="x", pady=5)
        self.main_app.theme_elements.append(self.new_mat_name)

        self.add_themed_label("Wattage (W):")
        self.new_mat_watt = tk.Entry(self.win, relief="flat")
        self.new_mat_watt.pack(fill="x", pady=5)
        self.main_app.theme_elements.append(self.new_mat_watt)

        self.add_themed_label("Price per Gram (Php):")
        self.new_mat_price = tk.Entry(self.win, relief="flat")
        self.new_mat_price.pack(fill="x", pady=5)
        self.main_app.theme_elements.append(self.new_mat_price)

        self.add_btn = tk.Button(
            self.win, text="+ Add Material", 
            command=self.save_material, 
            relief="flat", font=("Arial", 10, "bold")
        )
        self.add_btn.pack(fill="x", pady=20)
        self.main_app.theme_elements.append(self.add_btn)

        ttk.Separator(self.win, orient='horizontal').pack(fill="x", pady=10)

        # --- REMOVE MATERIAL SECTION ---
        self.add_themed_label("Remove Material", is_header=True)
        
        self.delete_combo = ttk.Combobox(self.win, state="readonly")
        self.delete_combo.pack(fill="x", pady=10)
        
        self.delete_btn = tk.Button(
            self.win, text="🗑 Delete Selected", 
            command=self.confirm_delete, 
            relief="flat", font=("Arial", 10, "bold")
        )
        self.delete_btn.pack(fill="x", pady=10)
        self.main_app.theme_elements.append(self.delete_btn)
        
        self.refresh_delete_list()

    def refresh_delete_list(self):
        try:
            materials = database.get_all_materials()
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            materials = []
        names = [m[0] for m in materials]
        self.delete_combo['values'] = names
        if names:
            self.delete_combo.current(0)
        else:
            self.delete_combo.set('')

    def save_material(self):
        name = self.new_mat_name.get().strip()
        if not name:
            messagebox.showwarning("Incomplete", "Please enter a material name.")
            return

        try:
            watt = float(self.new_mat_watt.get())
            price = float(self.new_mat_price.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Wattage and Price must be valid numbers.")
            return

        if watt <= 0 or price <= 0:
            messagebox.showwarning("Invalid Input", "Wattage and Price must be greater than zero.")
            return

        try:
            database.add_material(name, watt, price)
        except ValueError as e:
            # Raised by database.add_material when the name already exists
            messagebox.showerror("Duplicate Material", str(e))
            return
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", f"Added {name}!")
        self.refresh_delete_list()
        self.main_app.refresh_material_dropdown()
        # Clear inputs
        self.new_mat_name.delete(0, tk.END)
        self.new_mat_watt.delete(0, tk.END)
        self.new_mat_price.delete(0, tk.END)

    def confirm_delete(self):
        target = self.delete_combo.get()
        if not target:
            return
        if messagebox.askyesno("Confirm", f"Delete '{target}' permanently?"):
            try:
                database.delete_material(target)
            except RuntimeError as e:
                messagebox.showerror("Database Error", str(e))
                return
            self.refresh_delete_list()
            self.main_app.refresh_material_dropdown()
            messagebox.showinfo("Success", "Material Removed")