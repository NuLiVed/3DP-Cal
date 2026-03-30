from tkinter import messagebox
from datetime import datetime
import database
import export

def generate_monthly_report():
    """Logic to fetch and export monthly data"""
    now = datetime.now()
    m = now.strftime('%m') 
    y = now.strftime('%Y')
    
    data = database.get_monthly_records(m, y)
    
    if not data:
        messagebox.showwarning("No Data", f"No orders found for {m}/{y}.")
        return False
    
    try:
        filepath = export.export_to_excel(m, y, data)
        messagebox.showinfo("Report Exported", f"Monthly report saved successfully!\nLocation: {filepath}")
        return True
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export: {e}")
        return False