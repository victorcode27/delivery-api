import database
import json
import datetime

# Helper to handle date serialization
def default_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def verify_structure():
    database.init_db()
    reports = database.get_reports()
    if not reports:
        print("No reports found.")
        return

    first_report = reports[0]
    print(json.dumps(first_report, default=str, indent=2))

if __name__ == "__main__":
    verify_structure()
