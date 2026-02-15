"""
PostgreSQL Schema Initialization Script
This script creates all tables in the delivery_db PostgreSQL database.
"""

import sys
import os

# Add current directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
import psycopg2
from psycopg2 import sql

print("=" * 80)
print("PostgreSQL Schema Initialization")
print("=" * 80)
print()

# Connection string to verify
connection_string = "postgresql://postgres:1234@localhost:5432/delivery_db"

# Expected tables (based on init_db() function)
expected_tables = [
    'users',
    'orders',  # This stores invoices
    'reports',
    'report_items',
    'settings',
    'trucks',
    'customer_routes',
    'manifest_events',
    'manifest_staging'
]

print("Step 1: Executing init_db() to create all tables...")
print("-" * 80)

try:
    # Execute the schema initialization
    init_db()
    print("[OK] init_db() executed successfully")
    print()
except Exception as e:
    print(f"[ERROR] Failed to execute init_db(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Step 2: Verifying table creation in PostgreSQL...")
print("-" * 80)

try:
    # Connect to delivery_db to verify tables
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    actual_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Tables found: {len(actual_tables)}")
    print()
    
    # Check each expected table
    all_exist = True
    for table in expected_tables:
        if table in actual_tables:
            # Count rows
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            count = cursor.fetchone()[0]
            print(f"  [+] {table}: {count} rows")
        else:
            print(f"  [X] {table}: MISSING")
            all_exist = False
    
    print()
    
    # Show any extra tables
    extra_tables = [t for t in actual_tables if t not in expected_tables]
    if extra_tables:
        print(f"Additional tables found: {', '.join(extra_tables)}")
        print()
    
    cursor.close()
    conn.close()
    
    # Final report
    print("=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    
    if all_exist:
        print("[SUCCESS] All expected tables have been created successfully!")
        print()
        print("Created tables:")
        for table in expected_tables:
            print(f"  - {table}")
        print()
        print("[OK] Step 1: Database 'delivery_db' exists")
        print("[OK] Step 2: All tables created via init_db()")
        print()
        print("Note: The 'orders' table stores both invoices and credit notes.")
        print("      'invoices' and 'manifest_invoices' are NOT separate tables.")
    else:
        print("[INCOMPLETE] Some tables are missing!")
        sys.exit(1)
    
    print("=" * 80)
    
except psycopg2.Error as e:
    print(f"[ERROR] Database connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
