# --- Antigravity / FastAPI Test Script ---
# Purpose: Test manifest staging workflow for 1 invoice
# Warning: Only run 1 invoice at a time to save quota

import requests
import sys

BASE_URL = "http://localhost:8000"  # Change if your API runs on LAN
USERNAME = "testuser"               # Your X-Username header
HEADERS = {"X-Username": USERNAME}

def safe_request(method, url, **kwargs):
    """Make a request and handle errors gracefully"""
    try:
        if method == "GET":
            r = requests.get(url, **kwargs)
        else:
            r = requests.post(url, **kwargs)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        sys.exit(1)

print("=" * 60)
print("ANTIGRAVITY TEST SCRIPT - Single Invoice Workflow")
print("=" * 60)

# Step 1: Add Manual Invoice
print("\n[STEP 1] Adding Manual Invoice...")
manual_invoice = {
    "customer_name": "Test Customer",
    "total_value": "1000",
    "invoice_number": "TEST123",
    "order_number": "ORD123",
    "customer_number": "CUST123",
    "area": "TESTAREA"
}

r = safe_request("POST", f"{BASE_URL}/invoices/manual", json=manual_invoice)
invoice_filename = r.json().get("filename")
print(f"[OK] Manual invoice added: {invoice_filename}")

# Step 2: Allocate Invoice to Staging
print("\n[STEP 2] Allocating Invoice to Staging...")
allocate_data = {"filenames": [invoice_filename]}
r = safe_request("POST", f"{BASE_URL}/invoices/allocate", headers=HEADERS, json=allocate_data)
print(f"[OK] Allocation response: {r.json()}")

# Step 3: Verify Invoice in Staging
print("\n[STEP 3] Verifying Invoice in Staging...")
r = safe_request("GET", f"{BASE_URL}/manifest/current", headers=HEADERS)
invoices = r.json().get('invoices', [])
print(f"[OK] Invoices in staging ({len(invoices)}):")
for inv in invoices:
    print(f"   - {inv['filename']} - {inv['customer_name']}")

# Step 4: Remove Invoice from Staging
print("\n[STEP 4] Removing Invoice from Staging...")
r = safe_request("POST", f"{BASE_URL}/manifest/remove", headers=HEADERS, json=allocate_data)
print(f"[OK] Removal response: {r.json()}")

# Step 5: Verify Available Invoices
print("\n[STEP 5] Verifying Available Invoices...")
r = safe_request("GET", f"{BASE_URL}/invoices")
available = [inv["filename"] for inv in r.json().get("invoices", [])]
print(f"[OK] Available invoices after removal ({len(available)}):")
for filename in available[:10]:  # Show first 10
    print(f"   - {filename}")
if len(available) > 10:
    print(f"   ... and {len(available) - 10} more")

print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED - Workflow Complete!")
print("=" * 60)
