import sqlite3

def init_vault():
    # Establishes connection to the database file (it creates it if it doesn't exist)
    conn = sqlite3.connect("hadesnet_vault.db")
    cursor = conn.cursor()
    
    print("🔱 HadesNet Database: Initializing structural tables...")
    
    # Create a table to store the historical logs of all document audits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_order_id TEXT,
            financial_total REAL,
            calculated_total REAL,
            variance REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("🔱 HadesNet Database: Structural tables verified and locked.")

if __name__ == "__main__":
    init_vault()