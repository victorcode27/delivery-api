
import sqlite3
import os

DB_PATH = r"c:\Users\Assault\OneDrive\Documents\Delivery Route\delivery.db"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Table Info: report_items ---")
    try:
        cursor.execute("PRAGMA table_info(report_items)")
        columns = cursor.fetchall()
        for col in columns:
            print(dict(col))
    except Exception as e:
        print(f"Error getting table info: {e}")

    print("\n--- Last 5 Report Items ---")
    try:
        cursor.execute("SELECT * FROM report_items ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error fetching data: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_db()
