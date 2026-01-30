"""
Frontend Simulation Test
Simulates exactly what the browser JavaScript would send
"""
import requests

# Simulate the exact URLSearchParams construction from dispatch_report.js
date_from = '2026-01-29'
date_to = '2026-01-29'

# Build params exactly as JavaScript does
params = {}
if date_from:
    params['date_from'] = date_from
if date_to:
    params['date_to'] = date_to
params['filter_type'] = 'dispatch'
params['limit'] = '50'
params['offset'] = '0'
params['sort_by'] = 'date_dispatched'
params['sort_order'] = 'DESC'

url = 'http://localhost:8000/reports/dispatched'

print("=" * 60)
print("FRONTEND SIMULATION TEST")
print("=" * 60)
print(f"URL: {url}")
print(f"Params: {params}")
print()

response = requests.get(url, params=params)
data = response.json()

print(f"Status: {response.status_code}")
print(f"Total: {data.get('total', 0)}")
print(f"Invoices returned: {len(data.get('invoices', []))}")
print()

if data.get('invoices'):
    print("First invoice:")
    print(f"  Invoice #: {data['invoices'][0].get('invoice_number')}")
    print(f"  Date Dispatched: {data['invoices'][0].get('date_dispatched')}")
    print(f"  Customer: {data['invoices'][0].get('customer_name')}")
