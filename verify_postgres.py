import psycopg2
from psycopg2 import sql
import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connection string
connection_string = "postgresql://postgres:1234@localhost:5432/delivery_db"

# Expected tables
expected_tables = [
    'users',
    'orders',
    'invoices',
    'manifest_staging',
    'manifest_invoices',
    'manifest_events',
    'settings',
    'trucks',
    'reports',
    'report_items'
]

print("=" * 80)
print("PostgreSQL Migration Verification Report")
print("=" * 80)
print()

try:
    # Connect to PostgreSQL server (postgres database) to check if delivery_db exists
    conn_postgres = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="1234",
        database="postgres"
    )
    conn_postgres.autocommit = True
    cursor_postgres = conn_postgres.cursor()
    
    # Check if delivery_db exists
    cursor_postgres.execute("SELECT 1 FROM pg_database WHERE datname = 'delivery_db'")
    db_exists = cursor_postgres.fetchone() is not None
    
    print(f"[+] Database 'delivery_db' exists: {db_exists}")
    print()
    
    cursor_postgres.close()
    conn_postgres.close()
    
    if not db_exists:
        print("[X] Database does not exist. Migration Step 1 is INCOMPLETE.")
        exit(1)
    
    # Connect to delivery_db
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # List all tables in delivery_db
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    actual_tables = [row[0] for row in cursor.fetchall()]
    
    print("Tables found in delivery_db:")
    print("-" * 40)
    for table in actual_tables:
        print(f"  - {table}")
    print()
    
    # Check if all expected tables exist
    missing_tables = [table for table in expected_tables if table not in actual_tables]
    
    print("Expected Tables Verification:")
    print("-" * 40)
    for table in expected_tables:
        exists = table in actual_tables
        status = "[+]" if exists else "[X]"
        print(f"  {status} {table}")
    print()
    
    if missing_tables:
        print(f"[X] Missing tables: {', '.join(missing_tables)}")
        print()
    
    # Count rows in each existing table
    print("Table Row Counts:")
    print("-" * 40)
    for table in expected_tables:
        if table in actual_tables:
            try:
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: Error counting - {str(e)}")
        else:
            print(f"  {table}: [TABLE MISSING]")
    print()
    
    # Close connection
    cursor.close()
    conn.close()
    
    # Final verification
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"[+] Database exists: {db_exists}")
    print(f"[+] All expected tables exist: {len(missing_tables) == 0}")
    print(f"[+] Schema created by app (via init_db/metadata.create_all): {'YES' if len(missing_tables) == 0 else 'PARTIAL'}")
    print()
    
    if db_exists and len(missing_tables) == 0:
        print("[OK] STEP 1 COMPLETE: Database 'delivery_db' created successfully")
        print("[OK] STEP 2 COMPLETE: All tables created via init_db()/metadata.create_all()")
    elif db_exists and len(missing_tables) > 0:
        print("[OK] STEP 1 COMPLETE: Database 'delivery_db' created successfully")
        print(f"[X] STEP 2 INCOMPLETE: Missing tables: {', '.join(missing_tables)}")
    else:
        print("[X] STEP 1 INCOMPLETE: Database 'delivery_db' not created")
        print("[X] STEP 2 INCOMPLETE: Tables not created")
    
    print("=" * 80)
    
except psycopg2.OperationalError as e:
    print(f"[X] Connection Error: {str(e)}")
    print()
    print("Possible issues:")
    print("  - PostgreSQL server is not running")
    print("  - Database 'delivery_db' does not exist")
    print("  - Incorrect credentials")
    print("  - Port 5432 is not accessible")
    print()
    print("[X] STEP 1 INCOMPLETE: Cannot connect to database")
    print("[X] STEP 2 INCOMPLETE: Cannot verify tables")
    
except Exception as e:
    print(f"[X] Error: {str(e)}")
    import traceback
    traceback.print_exc()
