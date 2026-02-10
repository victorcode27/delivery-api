import sqlite3
import os

# Clean orphaned staging rows
DB_PATH = os.path.join(os.path.dirname(__file__), "delivery.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== CLEANING ORPHANED STAGING ROWS ===")

# 1. Delete staging rows for already-finalized invoices
cursor.execute("""
    DELETE FROM manifest_staging 
    WHERE invoice_id IN (
        SELECT id FROM orders WHERE is_allocated = 1 AND manifest_number IS NOT NULL
    )
""")
print(f"Deleted {cursor.rowcount} staging rows for already-finalized invoices")

# 2. Delete staging rows with corrupted session_ids
cursor.execute("DELETE FROM manifest_staging WHERE session_id LIKE '%object%'")
print(f"Deleted {cursor.rowcount} staging rows with corrupted session_id")

conn.commit()

print("\n=== REMAINING STAGING ROWS ===")
cursor.execute("SELECT session_id, COUNT(*) as count FROM manifest_staging GROUP BY session_id")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  Session '{row[0]}': {row[1]} rows")
else:
    print("  None (staging table is clean)")

conn.close()
print("\nDone!")
