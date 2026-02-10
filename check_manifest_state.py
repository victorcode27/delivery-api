import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "delivery.db")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== MANIFEST STAGING TABLE ===")
cursor.execute("SELECT COUNT(*) as count FROM manifest_staging")
print(f"Total staging rows: {cursor.fetchone()['count']}")

cursor.execute("SELECT session_id, COUNT(*) as count FROM manifest_staging GROUP BY session_id")
for row in cursor.fetchall():
    print(f"  Session '{row['session_id']}': {row['count']} rows")

print("\n=== FINALIZED MANIFESTS ===")
cursor.execute("SELECT manifest_number, COUNT(*) as count FROM orders WHERE is_allocated=1 AND manifest_number IS NOT NULL GROUP BY manifest_number ORDER BY manifest_number DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"  Manifest '{row['manifest_number']}': {row['count']} invoices")

print("\n=== LATEST MANIFEST ===")
cursor.execute("SELECT manifest_number FROM reports ORDER BY id DESC LIMIT 1")
latest = cursor.fetchone()
if latest:
    manifest_num = latest['manifest_number']
    print(f"Latest finalized manifest: {manifest_num}")
    
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE manifest_number=? AND is_allocated=1 AND type='INVOICE'", (manifest_num,))
    print(f"  Finalized invoices: {cursor.fetchone()['count']}")

conn.close()
