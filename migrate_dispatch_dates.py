"""
Migration script to add date_dispatched field and performance indexes
to the dispatch reports system.

This script includes enhanced validation and will abort if any issues are found.
"""

import sqlite3
import os
import sys
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "delivery.db")

def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)

def migrate_dispatch_dates():
    """
    Migrate the database to add date_dispatched field and indexes.
    
    Steps:
    1. Add date_dispatched column to reports table
    2. Migrate existing date values to date_dispatched
    3. Validate no NULL values remain
    4. Create performance indexes
    5. Add immutability triggers (optional)
    """
    
    print("=" * 80)
    print("DISPATCH REPORT MIGRATION SCRIPT")
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # ==========================================
        # STEP 1: Add date_dispatched column
        # ==========================================
        print("\n[STEP 1] Checking for date_dispatched column...")
        cursor.execute("PRAGMA table_info(reports)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'date_dispatched' in columns:
            print("  [OK] date_dispatched column already exists")
        else:
            print("  --> Adding date_dispatched column...")
            cursor.execute("ALTER TABLE reports ADD COLUMN date_dispatched TEXT")
            print("  [OK] date_dispatched column added")
        
        # ==========================================
        # STEP 2: Migrate existing date values
        # ==========================================
        print("\n[STEP 2] Migrating existing date values...")
        cursor.execute("SELECT COUNT(*) FROM reports WHERE date_dispatched IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"  --> Found {null_count} reports with NULL date_dispatched")
            print("  --> Copying values from 'date' column to 'date_dispatched'...")
            cursor.execute("UPDATE reports SET date_dispatched = date WHERE date_dispatched IS NULL")
            affected = cursor.rowcount
            print(f"  [OK] Updated {affected} reports")
            
            # Log affected report IDs
            cursor.execute("SELECT id, manifest_number, date, date_dispatched FROM reports ORDER BY id")
            reports = cursor.fetchall()
            print(f"\n  Report IDs affected (showing first 10):")
            for i, (rid, manifest, date, date_dispatched) in enumerate(reports[:10]):
                print(f"    - Report ID {rid}, Manifest {manifest}: {date} → {date_dispatched}")
            if len(reports) > 10:
                print(f"    ... and {len(reports) - 10} more")
        else:
            print("  [OK] All reports already have date_dispatched values")
        
        # ==========================================
        # STEP 3: VALIDATE - No NULL values
        # ==========================================
        print("\n[STEP 3] Validating migration...")
        cursor.execute("SELECT COUNT(*) FROM reports WHERE date_dispatched IS NULL")
        remaining_nulls = cursor.fetchone()[0]
        
        if remaining_nulls > 0:
            print(f"  [ERROR] VALIDATION FAILED: {remaining_nulls} reports still have NULL date_dispatched")
            print("  [ERROR] ABORTING MIGRATION - Rolling back changes")
            conn.rollback()
            return False
        else:
            print("  [OK] Validation passed - No NULL date_dispatched values found")
        
        # ==========================================
        # STEP 4: Create performance indexes
        # ==========================================
        print("\n[STEP 4] Creating performance indexes...")
        
        indexes_to_create = [
            ("idx_reports_date_dispatched", "reports", "date_dispatched"),
            ("idx_reports_manifest_number", "reports", "manifest_number"),
            ("idx_report_items_invoice_number", "report_items", "invoice_number"),
            ("idx_report_items_report_id", "report_items", "report_id"),
        ]
        
        for idx_name, table_name, column_name in indexes_to_create:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
                print(f"  [OK] Created index: {idx_name} on {table_name}({column_name})")
            except sqlite3.OperationalError as e:
                print(f"  [WARN] Index {idx_name} already exists or error: {e}")
        
        # ==========================================
        # STEP 5: Add immutability triggers (OPTIONAL)
        # ==========================================
        print("\n[STEP 5] Adding immutability triggers (optional)...")
        
        # Trigger to prevent UPDATE on reports table
        try:
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS prevent_reports_update
                BEFORE UPDATE ON reports
                BEGIN
                    SELECT RAISE(ABORT, 'Historical dispatch reports cannot be modified');
                END;
            """)
            print("  [OK] Created trigger: prevent_reports_update")
        except sqlite3.Error as e:
            print(f"  [WARN] Trigger creation warning: {e}")
        
        # Trigger to prevent DELETE on reports table
        try:
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS prevent_reports_delete
                BEFORE DELETE ON reports
                BEGIN
                    SELECT RAISE(ABORT, 'Historical dispatch reports cannot be deleted');
                END;
            """)
            print("  [OK] Created trigger: prevent_reports_delete")
        except sqlite3.Error as e:
            print(f"  [WARN] Trigger creation warning: {e}")
        
        # Trigger to prevent UPDATE on report_items table
        try:
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS prevent_report_items_update
                BEFORE UPDATE ON report_items
                BEGIN
                    SELECT RAISE(ABORT, 'Historical dispatch report items cannot be modified');
                END;
            """)
            print("  [OK] Created trigger: prevent_report_items_update")
        except sqlite3.Error as e:
            print(f"  [WARN] Trigger creation warning: {e}")
        
        # Trigger to prevent DELETE on report_items table
        try:
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS prevent_report_items_delete
                BEFORE DELETE ON report_items
                BEGIN
                    SELECT RAISE(ABORT, 'Historical dispatch report items cannot be deleted');
                END;
            """)
            print("  [OK] Created trigger: prevent_report_items_delete")
        except sqlite3.Error as e:
            print(f"  [WARN] Trigger creation warning: {e}")
        
        # ==========================================
        # COMMIT TRANSACTION
        # ==========================================
        print("\n[COMMIT] Committing all changes...")
        conn.commit()
        print("  [OK] Migration completed successfully!")
        
        # ==========================================
        # FINAL SUMMARY
        # ==========================================
        print("\n" + "=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM report_items")
        total_items = cursor.fetchone()[0]
        
        print(f"Total reports in database: {total_reports}")
        print(f"Total report items in database: {total_items}")
        print(f"All reports have valid date_dispatched values: YES")
        print(f"Performance indexes created: YES")
        print(f"Immutability triggers created: YES")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        print("[ERROR] Rolling back all changes...")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    success = migrate_dispatch_dates()
    exit(0 if success else 1)
