import requests
import json

API_URL = "http://localhost:8000"

print("--- Fetching Reports from API ---")
try:
    response = requests.get(f"{API_URL}/reports")
    data = response.json()
    
    reports = data.get('reports', [])
    print(f"Found {len(reports)} reports\n")
    
    if reports:
        # Show first report structure
        first_report = reports[0]
        print("First Report Structure:")
        print(json.dumps(first_report, indent=2))
        
        if 'invoices' in first_report and first_report['invoices']:
            print("\nFirst Invoice in Report:")
            print(json.dumps(first_report['invoices'][0], indent=2))
    else:
        print("No reports found")
        
except Exception as e:
    print(f"Error: {e}")
