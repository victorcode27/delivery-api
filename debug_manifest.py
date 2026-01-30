import database
import json

def debug_manifest_details():
    database.init_db()
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get latest report/manifest
    cursor.execute("SELECT manifest_number FROM reports ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    
    if not row:
        print("No manifests found.")
        return

    manifest_number = row['manifest_number']
    print(f"Testing Manifest: {manifest_number}")
    
    # Call the function used by API
    details = database.get_manifest_details(manifest_number)
    
    print(json.dumps(details, default=str, indent=2))
    
if __name__ == "__main__":
    debug_manifest_details()
