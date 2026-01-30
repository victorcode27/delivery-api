"""
Test script to verify new dispatch report endpoints.
"""

import requests
import json

API_URL = "http://localhost:8000"

print("=" * 80)
print("TESTING NEW DISPATCH REPORT ENDPOINTS")
print("=" * 80)

# Test 1: Get dispatched invoices (no filters)
print("\n[TEST 1] Get dispatched invoices (no filters)...")
try:
    response = requests.get(f"{API_URL}/reports/dispatched")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {response.status_code}")
        print(f"  Total invoices: {data.get('total', 0)}")
        print(f"  Returned: {len(data.get('invoices', []))}")
        print(f"  Page: {data.get('page', 0)}, Limit: {data.get('limit', 50)}")
        
        if data.get('invoices'):
            first = data['invoices'][0]
            print(f"  Sample invoice:")
            print(f"    - Invoice #: {first.get('invoice_number')}")
            print(f"    - Order #: {first.get('order_number')}")
            print(f"    - Customer: {first.get('customer_name')}")
            print(f"    - Manifest: {first.get('manifest_number')}")
            print(f"    - Driver: {first.get('driver')}")
            print(f"    - Date Dispatched: {first.get('date_dispatched')}")
    else:
        print(f"  [ERROR] Status: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Get dispatched invoices with date filter
print("\n[TEST 2] Get dispatched invoices with date filter...")
try:
    response = requests.get(f"{API_URL}/reports/dispatched?date_from=2026-01-26&date_to=2026-01-26")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {response.status_code}")
        print(f"  Total invoices for 2026-01-26: {data.get('total', 0)}")
    else:
        print(f"  [ERROR] Status: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 3: Get dispatched invoices with search
print("\n[TEST 3] Get dispatched invoices with search...")
try:
    response = requests.get(f"{API_URL}/reports/dispatched?search=BINV")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {response.status_code}")
        print(f"  Total matching 'BINV': {data.get('total', 0)}")
        if data.get('invoices'):
            print(f"  Sample results:")
            for inv in data['invoices'][:3]:
                print(f"    - {inv.get('invoice_number')} ({inv.get('customer_name')})")
    else:
        print(f"  [ERROR] Status: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 4: Get dispatched invoices with pagination
print("\n[TEST 4] Get dispatched invoices with pagination...")
try:
    response = requests.get(f"{API_URL}/reports/dispatched?limit=5&offset=0")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {response.status_code}")
        print(f"  Total: {data.get('total', 0)}")
        print(f"  Returned (page 1): {len(data.get('invoices', []))}")
        
        # Get next page
        response2 = requests.get(f"{API_URL}/reports/dispatched?limit=5&offset=5")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"  Returned (page 2): {len(data2.get('invoices', []))}")
    else:
        print(f"  [ERROR] Status: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 5: Get outstanding orders
print("\n[TEST 5] Get outstanding orders...")
try:
    response = requests.get(f"{API_URL}/reports/outstanding")
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Status: {response.status_code}")
        print(f"  Total outstanding orders: {data.get('count', 0)}")
        
        if data.get('orders'):
            print(f"  Sample outstanding orders:")
            for order in data['orders'][:5]:
                print(f"    - Invoice: {order.get('invoice_number')}, Order: {order.get('order_number')}")
                print(f"      Customer: {order.get('customer_name')}, Date: {order.get('invoice_date')}")
    else:
        print(f"  [ERROR] Status: {response.status_code}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 6: Verify immutability protection
print("\n[TEST 6] Verify immutability protection...")
try:
    import sqlite3
    conn = sqlite3.connect("C:\\\\Users\\\\Assault\\\\OneDrive\\\\Documents\\\\Delivery Route\\\\delivery.db")
    cursor = conn.cursor()
    
    # Try to update a report
    try:
        cursor.execute("UPDATE reports SET driver = 'HACKED' WHERE id = 1")
        conn.commit()
        print("  [WARNING] Update succeeded - triggers may not be working")
    except sqlite3.Error as e:
        print(f"  [OK] Update blocked by trigger: {str(e)[:100]}")
    
    # Try to delete a report
    try:
        cursor.execute("DELETE FROM reports WHERE id = 1")
        conn.commit()
        print("  [WARNING] Delete succeeded - triggers may not be working")
    except sqlite3.Error as e:
        print(f"  [OK] Delete blocked by trigger: {str(e)[:100]}")
    
    conn.close()
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
