import sqlite3
import os
import json

DB_PATH = "delivery.db"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Last 5 Reports ---")
    cursor.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 5")
    reports = cursor.fetchall()
    
    for r in reports:
        print(f"ID: {r['id']}, Manifest: {r['manifest_number']}, Reg: {r['reg_number']}, Date: {r['date']}")
        
        print(f"  Items for Report {r['id']}:")
        cursor.execute("SELECT * FROM report_items WHERE report_id = ?", (r['id'],))
        items = cursor.fetchall()
        if not items:
            print("    (No items)")
        for i in items:
            print(f"    - Inv: {i['invoice_number']}, Order: {i['order_number']}, Cust: {i['customer_name']}, Date: {i['invoice_date']}")
    
    conn.close()

if __name__ == "__main__":
    inspect_db()
