import requests
import json

# Test the API endpoint with date filters
url = "http://localhost:8000/reports/dispatched"

# Test 1: No filters
print("=" * 60)
print("TEST 1: No filters")
print("=" * 60)
response = requests.get(url)
data = response.json()
print(f"Status: {response.status_code}")
print(f"Total invoices: {data.get('total', 0)}")
print(f"Returned invoices: {len(data.get('invoices', []))}")
print()

# Test 2: With date filter
print("=" * 60)
print("TEST 2: With date filter (2026-01-29)")
print("=" * 60)
params = {
    'date_from': '2026-01-29',
    'date_to': '2026-01-29'
}
print(f"Request URL: {url}?{requests.compat.urlencode(params)}")
response = requests.get(url, params=params)
data = response.json()
print(f"Status: {response.status_code}")
print(f"Total invoices: {data.get('total', 0)}")
print(f"Returned invoices: {len(data.get('invoices', []))}")
if data.get('invoices'):
    print(f"First invoice: {json.dumps(data['invoices'][0], indent=2)}")
print()

# Test 3: Check old /reports endpoint
print("=" * 60)
print("TEST 3: Old /reports endpoint with date filter")
print("=" * 60)
old_url = "http://localhost:8000/reports"
response = requests.get(old_url, params=params)
data = response.json()
print(f"Status: {response.status_code}")
print(f"Total reports: {data.get('count', 0)}")
print(f"Returned reports: {len(data.get('reports', []))}")
if data.get('reports'):
    print(f"First report has {len(data['reports'][0].get('invoices', []))} invoices")
