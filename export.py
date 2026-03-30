from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas 
from PIL import Image, ImageDraw, ImageFont
import csv
import os
# Import the absolute paths from your main config
from config import RECEIPTS_DIR, REPORTS_DIR 

def generate_pdf(f_base, mat, w, h, rate_label, total_cost):
    """Generates a PDF receipt using the absolute path."""
    # Use the REGISTERED Receipts directory
    filepath = os.path.join(RECEIPTS_DIR, f"{f_base}.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    c.setFont("Courier-Bold", 16)
    c.drawString(100, height - 80, "3D PRINT HUB - COST BREAKDOWN")
    c.setFont("Courier", 12)
    c.drawString(100, height - 100, "-----------------------------")
    
    y_position = height - 130
    lines = [
        f"Order ID:   {f_base.split('_')[1]}",
        f"Material:   {mat}",
        f"Weight:     {w:.0f}g",
        f"Print Time: {h:.2f} hrs",
        "",
        f"Rate Tier: {rate_label}",
        "----------------------------------",
        f"TOTAL COST: Php {total_cost:.2f}",
        "----------------------------------"
    ]

    for line in lines:
        c.drawString(100, y_position, line)
        y_position -= 20

    c.setFont("Courier-Oblique", 10)
    c.drawString(100, y_position - 20, "Thank you for your business!")
    c.save()
    
def generate_png(f_base, mat, w, h, rate_label, total_cost):
    """Generates a PNG receipt saved in the Receipts folder."""
    # CHANGED: Save PNGs to 'Receipts' folder instead of a generic 'Exports'
    filepath = os.path.join(RECEIPTS_DIR, f"{f_base}.png")
    
    img = Image.new('RGB', (400, 500), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    try:
        # Note: 'cour.ttf' is standard on Windows. 
        # For EXE, usually better to bundle the .ttf if you want it to look the same everywhere.
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_reg = ImageFont.truetype("cour.ttf", 16)
    except:
        font_bold = ImageFont.load_default()
        font_reg = ImageFont.load_default()

    d.text((20, 40), "3D PRINT RECEIPT", fill=(0, 0, 0), font=font_bold)
    d.line((20, 70, 380, 70), fill=(200, 200, 200), width=2)

    content = [
        f"Order: #{f_base.split('_')[1]}",
        f"Material: {mat}",
        f"Weight: {w:.0f}g",
        f"Time: {h:.2f} hrs",
        "",
        f"Tier: {rate_label}",
        "--------------------------",
        f"TOTAL: Php {total_cost:.2f}"
    ]

    y_text = 100
    for line in content:
        d.text((40, y_text), line, fill=(50, 50, 50), font=font_reg)
        y_text += 30

    img.save(filepath)

def export_to_excel(month, year, data):
    """Saves monthly report into the absolute Reports directory."""
    filename = os.path.join(REPORTS_DIR, f"Monthly_Report_{year}_{month}.csv")
    
    headers = ["Order ID", "Date/Time", "Material", "Weight (g)", "Print Time (hrs)", "Total Price (Php)"]

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f"3DP PRINT HUB - MONTHLY REVENUE REPORT ({month}/{year})"])
        writer.writerow([]) 
        writer.writerow(headers)
        writer.writerows(data)
        
        total_revenue = sum(row[5] for row in data)
        writer.writerow([])
        writer.writerow(["", "", "", "", "GRAND TOTAL:", f"Php {total_revenue:.2f}"])

    return filename