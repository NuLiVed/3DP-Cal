import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import database
import export

class PreviewWindow:
    def __init__(self, main_app, mat, w, h, rate_label, total_cost, order_id):
        self.main_app = main_app
        self.colors = main_app.get_theme_colors()
        
        # Data storage for export logic
        self.params = (mat, w, h, rate_label, total_cost, order_id)
        
        # Window Setup
        self.win = tk.Toplevel(main_app.root)
        self.win.title(f"Cost Breakdown - Order # {order_id}")
        self.win.geometry("400x550")
        self.win.configure(padx=30, pady=20)
        
        # Register window for theme
        self.main_app.theme_elements.append(self.win)
        
        self.create_widgets()
        
        # Force immediate theme apply so it matches current mode
        self.main_app.apply_theme()

    def create_widgets(self):
        mat, w, h, rate_label, total_cost, order_id = self.params
        
        # --- RECEIPT FORMATTING ---
        header = f"3d Print Job Cost Breakdown \n{'-'*28} \nDate: {datetime.now().strftime('%Y-%m-%d')}"
        body = f"\nMaterial: {mat} \nWeight: {w:.2f}g \nPrint Time: {h:.2f} hrs \n\nRate: {rate_label}\n"
        footer = f"\n{'-'*28}\n TOTAL: Php {total_cost:.2f} \n{'-'*28}\n Thank you!"
        
        # Main Receipt Label
        self.receipt_lbl = tk.Label(
            self.win, text=header + body + footer, 
            font=("Courier", 12), justify="left"
        )
        self.receipt_lbl.pack(pady=20)
        self.main_app.theme_elements.append(self.receipt_lbl)

        # Button Container
        self.btn_container = tk.Frame(self.win)
        self.btn_container.pack(pady=10)
        self.main_app.theme_elements.append(self.btn_container)

        # PDF Export Button (Registered)
        self.pdf_btn = tk.Button(
            self.btn_container, text="📄 Export as PDF",
            command=lambda: self.handle_export("PDF"),
            font=("Arial", 10, "bold"), width=20, pady=8, cursor="hand2", relief="flat"
        )
        self.pdf_btn.pack(pady=5)
        self.main_app.theme_elements.append(self.pdf_btn)

        # PNG Export Button (Registered)
        self.img_btn = tk.Button(
            self.btn_container, text="🖼️ Save as Image", 
            command=lambda: self.handle_export("Image"),
            font=("Arial", 10, "bold"), width=20, pady=8, cursor="hand2", relief="flat"
        )        
        self.img_btn.pack(pady=5)
        self.main_app.theme_elements.append(self.img_btn)

    def handle_export(self, export_type):
        mat, w, h, rate_label, total_cost, order_id = self.params
        f_base = f"Receipt_Order_{order_id}_{mat}"
        
        try:
            ext = ".pdf" if export_type == "PDF" else ".png"
            filename_full = f_base + ext
            
            if export_type == "PDF":
                export.generate_pdf(f_base, mat, w, h, rate_label, total_cost)
            else: 
                export.generate_png(f_base, mat, w, h, rate_label, total_cost)
                
            database.save_receipt(f"Tier: {rate_label}", filename_full, mat, w, h, total_cost)
            
            messagebox.showinfo("Export Successful", f"Order #{order_id} exported as {export_type}")
            self.win.destroy() 
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export {export_type}: {e}")