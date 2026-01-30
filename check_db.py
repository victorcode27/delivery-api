
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "delivery.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Inspecting Settings Categories ---")
try:
    for category in ['driver', 'assistant', 'checker']:
        cursor.execute("SELECT * FROM settings WHERE category = ?", (category,))
        rows = cursor.fetchall()
        print(f"Category '{category}': {len(rows)} entries")
        for row in rows:
            print(f"  - {row['value']}")

except Exception as e:
    print(f"Error: {e}")

conn.close()
