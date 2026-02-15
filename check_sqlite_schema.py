import sqlite3

conn = sqlite3.connect("Delivery.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(reports)")
columns = cursor.fetchall()

print("SQLite reports table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
