# Diagnostic script to verify staging removal bug
import sqlite3
import requests

DB_PATH = r"C:\Users\Assault\OneDrive\Documents\Delivery Route\invoices.db"
BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
HEADERS = {"X-Username": USERNAME}

print("=" * 60)
print("STAGING REMOVAL BUG DIAGNOSTIC")
print("=" * 60)

# Create a manual invoice
print("\n[1] Creating manual test invoice...")
manual_invoice = {
    "customer_name": "DIAGNOSTIC Test Customer",
    "total_value": "999.99",
    "invoice_number": "DIAG001",
    "order_number": "DIAGORD001",
    "customer_number": "DIAGCUST001",
    "area": "DIAGNOSTIC"
}

r = requests.post(f"{BASE_URL}/invoices/manual", json=manual_invoice)
filename = r.json().get("filename")
print(f"   Created: {filename}")

# Check database state BEFORE allocation
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n[2] Database state BEFORE allocation:")
cursor.execute("SELECT filename, is_allocated, manifest_number FROM orders WHERE filename = ?", (filename,))
row = cursor.fetchone()
if row:
    print(f"   is_allocated: {row['is_allocated']}")
    print(f"   manifest_number: {row['manifest_number']}")

# Allocate to staging
print("\n[3] Allocating invoice to staging...")
r = requests.post(f"{BASE_URL}/invoices/allocate", headers=HEADERS, json={"filenames": [filename]})
print(f"   Response: {r.json()}")

# Check database state AFTER allocation
print("\n[4] Database state AFTER allocation:")
cursor.execute("SELECT filename, is_allocated, manifest_number FROM orders WHERE filename = ?", (filename,))
row = cursor.fetchone()
if row:
    print(f"   is_allocated: {row['is_allocated']}")
    print(f"   manifest_number: {row['manifest_number']}")

cursor.execute("SELECT COUNT(*) as count FROM manifest_staging WHERE invoice_id = (SELECT id FROM orders WHERE filename = ?)", (filename,))
staging_count = cursor.fetchone()['count']
print(f"   manifest_staging records: {staging_count}")

# Check if invoice appears in /invoices endpoint
print("\n[5] Checking /invoices endpoint...")
r = requests.get(f"{BASE_URL}/invoices")
available = [inv["filename"] for inv in r.json().get("invoices", [])]
is_available = filename in available
print(f"   Invoice in available list: {is_available}")
print(f"   Total available invoices: {len(available)}")

# Remove from staging
print("\n[6] Removing invoice from staging...")
r = requests.post(f"{BASE_URL}/manifest/remove", headers=HEADERS, json={"filenames": [filename]})
print(f"   Response: {r.json()}")

# Check database state AFTER removal
print("\n[7] Database state AFTER removal:")
cursor.execute("SELECT filename, is_allocated, manifest_number FROM orders WHERE filename = ?", (filename,))
row = cursor.fetchone()
if row:
    print(f"   is_allocated: {row['is_allocated']}")
    print(f"   manifest_number: {row['manifest_number']}")

cursor.execute("SELECT COUNT(*) as count FROM manifest_staging WHERE invoice_id = (SELECT id FROM orders WHERE filename = ?)", (filename,))
staging_count = cursor.fetchone()['count']
print(f"   manifest_staging records: {staging_count}")

# Check if invoice appears in /invoices endpoint AFTER removal
print("\n[8] Checking /invoices endpoint AFTER removal...")
r = requests.get(f"{BASE_URL}/invoices")
available = [inv["filename"] for inv in r.json().get("invoices", [])]
is_available = filename in available
print(f"   Invoice in available list: {is_available}")
print(f"   Total available invoices: {len(available)}")

# Cleanup
print("\n[9] Cleaning up test invoice...")
cursor.execute("DELETE FROM orders WHERE filename = ?", (filename,))
conn.commit()

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
print("\nBUG ANALYSIS:")
print("If is_allocated remains 1 or manifest_number is not NULL")
print("after removal, that's the bug causing invoices to disappear.")
print("=" * 60)

conn.close()
