
import sqlite3
import json
import requests

API_URL = "http://localhost:8000"

def migrate_settings(json_data):
    if not json_data:
        return

    # Migrate Settings Lists
    for category in ['drivers', 'assistants', 'checkers', 'routes']:
        items = json_data.get(category, [])
        for item in items:
            print(f"Adding {category}: {item}")
            requests.post(f"{API_URL}/settings", json={"category": category, "value": item})

    # Migrate Trucks
    trucks = json_data.get('trucks', [])
    for truck in trucks:
        print(f"Adding truck: {truck.get('reg')}")
        requests.post(f"{API_URL}/trucks", json={
            "reg": truck.get('reg'),
            "driver": truck.get('driver'),
            "assistant": truck.get('assistant'),
            "checker": truck.get('checker')
        })

    # Migrate Customer Routes
    routes = json_data.get('customerRoutes', {})
    for customer, route in routes.items():
        print(f"Adding route for {customer}: {route}")
        requests.post(f"{API_URL}/customer-routes", json={
            "customer_name": customer,
            "route_name": route
        })

def migrate_reports(reports_data):
    if not reports_data:
        return
        
    for report in reports_data:
        print(f"Adding report: {report.get('manifestNumber')}")
        requests.post(f"{API_URL}/reports", json=report)

print("Migration script helper loaded. Copy your localStorage data to use functions.")
