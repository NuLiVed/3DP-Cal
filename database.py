import sqlite3
import os
from datetime import datetime

# Defined Path to database file
DB_Path = "Data/3DP_Database.db"

# Function to Initialize Database and Create Tables if they don't exist
def initialize_database():
    
    # Check if Data Directory exists, if not create one
    if not os.path.exists('Data'):
        os.makedirs('Data')
    
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # Global Settings (Adjustable Settings for Meralco Rate and Setup Fee)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            meralco_rate REAL,
            setup_fee REAL
        )
    ''')
    
    # Materials Table (Stores Material Name, Wattage, and Price per Gram)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            wattage REAL,
            price_per_g REAL
        )
    ''')
    
    # Receipts Table (Stores Receipt Data, Filename, Material Used, Weight, Hours, and Total Cost)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            filename TEXT,
            material TEXT,
            weight REAL,
            hours REAL,
            total_cost REAL,
            date_timestamp TEXT
        )
    ''')
    
    # Default Settings 
    
    # Global Default Settings (Meralco Rate and Setup Fee)
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (id, meralco_rate, setup_fee) VALUES (?, ?, ?)", (1, 20.0, 50.0))
        
    # Default Materials
    cursor.execute("SELECT COUNT(*) FROM materials")
    if cursor.fetchone()[0] == 0:
        default_materials = [
            ("PLA", 120.0, 1.56),
            ("PETG", 140.0, 2.47)
        ]
        cursor.executemany("INSERT INTO materials (name, wattage, price_per_g) VALUES (?, ?, ?)", default_materials)
        
    conn.commit()
    conn.close()

# Function to Retrieve All Materials from Database
def get_all_materials():
    """Returns a list of all materials in the database for dropdown menu"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, wattage, price_per_g FROM materials")
    material_data = cursor.fetchall()
    conn.close()
    
    # Returns a list of containing material name, wattage, and price per gram for each material in the database
    return material_data 

# Function to Add a New Material to the Database
def add_material(name, wattage, price_per_g):
    """Adds a new material to the database"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO materials (name, wattage, price_per_g) VALUES (?, ?, ?)", (name, wattage, price_per_g))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Material '{name}' already registered!")
    conn.close()
    
def delete_material(name):
    """Removes a material from the database by name"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    
def get_settings():
    """Returns the current global settings (Meralco Rate and Setup Fee) from database"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    cursor.execute("SELECT meralco_rate, setup_fee FROM settings WHERE id = 1")
    settings = cursor.fetchone()
    conn.close()
    return settings

def update_settings(meralco_rate, setup_fee):
    """Updates the global settings (Meralco Rate and Setup Fee) in the database"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE settings
        SET meralco_rate = ?,
        setup_fee = ?,
        WHERE id = 1
    """, (meralco_rate, setup_fee))
    conn.commit()
    conn.close()
    
def get_next_order_id():
    """Look at the last ID in the table and add 1"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM receipts")
    last_id = cursor.fetchone()[0]
    conn.close()
    
    # If table is empty, start at 100 (or 1)
    return (last_id + 1) if last_id else 100

def save_receipt(data, filename, material, weight, hours, total_cost):
    """Saves receipt data to the database with a timestamp"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert Receipt Data into Database
    query = """
    INSERT INTO receipts (data, filename, material, weight, hours, total_cost, date_timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # Execute query with provided data and commit changes
    cursor.execute(query, (data, filename, material, weight, hours, total_cost, timestamp))
    conn.commit()
    conn.close()
    
def get_last_receipt():
    """Fetches the most recent entry from the receipts table"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    # Select the very last row added based on the auto-increment ID
    cursor.execute("SELECT material, weight, hours FROM receipts ORDER BY id DESC LIMIT 1")
    last_entry = cursor.fetchone()
    conn.close()
    return last_entry # Returns (material, weight, hours) or None

def get_monthly_records(month, year):
    """Fetches all receipt records for a specific month/year"""
    conn = sqlite3.connect(DB_Path)
    cursor = conn.cursor()
    
    # Filter by month and year using strftime to extract month and year from date_timestamp
    query = """
        SELECT id, date_timestamp, material, weight, hours, total_cost 
        FROM receipts 
        WHERE strftime('%m', date_timestamp) = ? 
        AND strftime('%Y', date_timestamp) = ?
    """
    cursor.execute(query, (month, year))
    rows = cursor.fetchall()
    conn.close()
    return rows