"""
Regression test for date filter fix.
Verifies that date_dispatched is populated correctly for all reports.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "delivery.db")

def test_date_dispatched_populated():
    """Verify that date_dispatched is populated when saving reports"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== Regression Test: Date Filter Fix ===\n")
    
    # Test 1: No NULL values
    cursor.execute("SELECT COUNT(*) FROM reports WHERE date_dispatched IS NULL")
    null_count = cursor.fetchone()[0]
    
    if null_count == 0:
        print("[PASS] Test 1: No reports have NULL date_dispatched")
    else:
        print(f"[FAIL] Test 1: Found {null_count} reports with NULL date_dispatched")
        conn.close()
        return False
    
    # Test 2: date_dispatched matches date for all reports
    cursor.execute("SELECT COUNT(*) FROM reports WHERE date != date_dispatched")
    mismatch_count = cursor.fetchone()[0]
    
    if mismatch_count == 0:
        print("[PASS] Test 2: All reports have date = date_dispatched")
    else:
        print(f"[FAIL] Test 2: Found {mismatch_count} reports where date != date_dispatched")
        conn.close()
        return False
    
    # Test 3: Verify total count
    cursor.execute("SELECT COUNT(*) FROM reports")
    total_count = cursor.fetchone()[0]
    print(f"[INFO] Total reports in database: {total_count}")
    
    # Test 4: Sample verification
    cursor.execute("SELECT manifest_number, date, date_dispatched FROM reports ORDER BY id DESC LIMIT 3")
    rows = cursor.fetchall()
    print("\n[INFO] Sample of recent reports:")
    print("Manifest        | Date       | DateDispatched")
    print("-" * 60)
    for row in rows:
        match = "OK" if row[1] == row[2] else "MISMATCH"
        print(f"{row[0]:15} | {row[1]:10} | {row[2]:14} [{match}]")
    
    conn.close()
    
    print("\n[SUCCESS] All regression tests passed!")
    return True

if __name__ == "__main__":
    success = test_date_dispatched_populated()
    exit(0 if success else 1)
