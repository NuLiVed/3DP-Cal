import sqlite3
from datetime import datetime
from config import DB_PATH  # Ensure this is defined as an absolute path in main.py

def get_connection():
    """Centrally managed connection using the absolute path"""
    return sqlite3.connect(DB_PATH)

def initialize_database():
    # We use get_connection() to ensure we use the correct path every time
    conn = get_connection()
    cursor = conn.cursor()
    
    # WAL mode improves performance and prevents "Database Locked" errors
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # 1. Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            meralco_rate REAL,
            setup_fee REAL
        )
    ''')
    
    # 2. Materials Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            wattage REAL,
            price_per_g REAL
        )
    ''')
    
    # 3. Receipts Table
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
    
    # --- Default Data Injection ---
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (id, meralco_rate, setup_fee) VALUES (1, 20.0, 50.0)")
        
    cursor.execute("SELECT COUNT(*) FROM materials")
    if cursor.fetchone()[0] == 0:
        default_materials = [("PLA", 120.0, 1.56), ("PETG", 140.0, 2.47)]
        cursor.executemany("INSERT INTO materials (name, wattage, price_per_g) VALUES (?, ?, ?)", default_materials)
        
    conn.commit()
    conn.close()

# --- DRY (Don't Repeat Yourself) Refactor ---
# Use get_connection() in all functions below to avoid path errors

def get_all_materials():
    """Returns materials sorted alphabetically by name."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Adding ORDER BY name makes the dropdown easier to navigate
        cursor.execute("SELECT name, wattage, price_per_g FROM materials ORDER BY name ASC")
        return cursor.fetchall()

def add_material(name, wattage, price_per_g):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO materials (name, wattage, price_per_g) VALUES (?, ?, ?)", (name, wattage, price_per_g))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Material '{name}' already exists.")

def delete_material(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materials WHERE name = ?", (name,))
        conn.commit()

def get_settings():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT meralco_rate, setup_fee FROM settings WHERE id = 1")
        return cursor.fetchone()

def update_settings(meralco_rate, setup_fee):
    with get_connection() as conn:
        cursor = conn.cursor()
        # FIXED: Removed the trailing comma after setup_fee = ?
        cursor.execute("""
            UPDATE settings
            SET meralco_rate = ?,
                setup_fee = ?
            WHERE id = 1
        """, (meralco_rate, setup_fee))
        conn.commit()

def get_next_order_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM receipts")
        last_id = cursor.fetchone()[0]
        return (last_id + 1) if last_id else 100

def save_receipt(data, filename, material, weight, hours, total_cost):
    with get_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
            INSERT INTO receipts (data, filename, material, weight, hours, total_cost, date_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (data, filename, material, weight, hours, total_cost, timestamp))
        conn.commit()

def get_last_receipt():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT material, weight, hours FROM receipts ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()

def get_monthly_records(month, year):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, date_timestamp, material, weight, hours, total_cost 
            FROM receipts 
            WHERE strftime('%m', date_timestamp) = ? 
            AND strftime('%Y', date_timestamp) = ?
        """
        cursor.execute(query, (month, year))
        return cursor.fetchall()