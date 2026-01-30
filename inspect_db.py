import sqlite3
import os

DB_PATH = r"C:\Users\Assault\OneDrive\Documents\Delivery Route\delivery.db"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Table Info: report_items ---")
    cursor.execute("PRAGMA table_info(report_items)")
    columns = cursor.fetchall()
    for col in columns:
        print(dict(col))

    print("\n--- Recent Orders (Top 5) ---")
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))

    conn.close()

if __name__ == "__main__":
    inspect_db()
