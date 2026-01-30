
import requests
import json

def check_api():
    try:
        response = requests.get("http://localhost:8000/reports")
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return

        data = response.json()
        reports = data.get('reports', [])
        
        if not reports:
            print("No reports found.")
            return

        print(f"Found {len(reports)} reports.")
        # Check the most recent report
        latest_report = reports[0] 
        print(f"\nLatest Report Manifest: {latest_report.get('manifest_number')}")
        
        invoices = latest_report.get('invoices', [])
        print(f"Found {len(invoices)} invoices in latest report.")
        
        if invoices:
            print("First Invoice Keys:", invoices[0].keys())
            print("First Invoice Data:", invoices[0])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
