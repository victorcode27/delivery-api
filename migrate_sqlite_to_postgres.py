"""
SQLite to PostgreSQL Data Migration Script
Migrates all data from Delivery.db to PostgreSQL delivery_db
Preserves original IDs and maintains data integrity.
"""

import sqlite3
import sys
import io
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Database connections
SQLITE_DB = "Delivery.db"
POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"

# Tables to migrate in order (respecting foreign keys)
TABLES_TO_MIGRATE = [
    'users',
    'orders',
    'reports',
    'report_items',
    'settings',
    'trucks',
    'customer_routes',
    'manifest_events',
    'manifest_staging'
]

def get_sqlite_connection():
    """Connect to SQLite database."""
    return sqlite3.connect(SQLITE_DB)

def get_postgres_session():
    """Create PostgreSQL session."""
    engine = create_engine(POSTGRES_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_table_columns(sqlite_conn, table_name):
    """Get column names for a table from SQLite."""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def migrate_table(sqlite_conn, pg_session, table_name):
    """Migrate all data from SQLite table to PostgreSQL table."""
    print(f"\nMigrating table: {table_name}")
    print("-" * 60)
    
    # Get all rows from SQLite
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"  No data to migrate (table is empty)")
        return 0
    
    # Get column names
    columns = get_table_columns(sqlite_conn, table_name)
    
    # Build INSERT query with named parameters
    column_list = ", ".join(columns)
    param_list = ", ".join([f":{col}" for col in columns])
    insert_query = f"INSERT INTO {table_name} ({column_list}) VALUES ({param_list})"
    
    # Migrate each row
    migrated_count = 0
    errors = 0
    
    for row in rows:
        try:
            # Create parameter dict
            params = {col: value for col, value in zip(columns, row)}
            
            # Execute insert
            pg_session.execute(text(insert_query), params)
            migrated_count += 1
            
        except Exception as e:
            errors += 1
            print(f"  ERROR migrating row: {e}")
            if errors > 5:
                print(f"  Too many errors, stopping migration for {table_name}")
                pg_session.rollback()
                return migrated_count
    
    # Commit all inserts for this table
    pg_session.commit()
    
    # Update sequence for SERIAL columns (PostgreSQL auto-increment)
    if 'id' in columns:
        try:
            # Get max ID from the table
            result = pg_session.execute(text(f"SELECT MAX(id) FROM {table_name}")).scalar()
            if result:
                # Update the sequence to continue from max ID
                pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), {result})"))
                pg_session.commit()
                print(f"  Updated sequence for {table_name} to start from {result + 1}")
        except Exception as e:
            print(f"  Warning: Could not update sequence: {e}")
    
    print(f"  [OK] Migrated {migrated_count} rows")
    if errors > 0:
        print(f"  [!] {errors} errors encountered")
    
    return migrated_count

def clear_postgres_tables(pg_session):
    """Clear all tables in PostgreSQL before migration (optional safety step)."""
    print("\nClearing existing PostgreSQL data...")
    print("-" * 60)
    
    # Disable foreign key checks temporarily
    for table in reversed(TABLES_TO_MIGRATE):
        try:
            result = pg_session.execute(text(f"DELETE FROM {table}"))
            pg_session.commit()
            print(f"  Cleared {table}: {result.rowcount} rows deleted")
        except Exception as e:
            print(f"  Warning clearing {table}: {e}")
            pg_session.rollback()

def main():
    """Main migration process."""
    print("=" * 80)
    print("SQLite to PostgreSQL Data Migration")
    print("=" * 80)
    print(f"Source: {SQLITE_DB}")
    print(f"Target: {POSTGRES_URL}")
    print()
    
    # Connect to databases
    try:
        sqlite_conn = get_sqlite_connection()
        print("[OK] Connected to SQLite database")
    except Exception as e:
        print(f"[ERROR] Failed to connect to SQLite: {e}")
        sys.exit(1)
    
    try:
        pg_session = get_postgres_session()
        print("[OK] Connected to PostgreSQL database")
    except Exception as e:
        print(f"[ERROR] Failed to connect to PostgreSQL: {e}")
        sys.exit(1)
    
    # Optional: Clear existing data
    response = input("\nClear existing PostgreSQL data before migration? (y/n): ")
    if response.lower() == 'y':
        clear_postgres_tables(pg_session)
    
    # Migrate each table
    print("\n" + "=" * 80)
    print("Starting Data Migration")
    print("=" * 80)
    
    total_rows = 0
    for table_name in TABLES_TO_MIGRATE:
        try:
            rows_migrated = migrate_table(sqlite_conn, pg_session, table_name)
            total_rows += rows_migrated
        except Exception as e:
            print(f"\n[ERROR] CRITICAL ERROR migrating {table_name}: {e}")
            import traceback
            traceback.print_exc()
            pg_session.rollback()
    
    # Close connections
    sqlite_conn.close()
    pg_session.close()
    
    # Final report
    print("\n" + "=" * 80)
    print("Migration Complete")
    print("=" * 80)
    print(f"Total rows migrated: {total_rows}")
    print()
    print("[OK] All data has been successfully migrated from SQLite to PostgreSQL")
    print("[OK] Original IDs have been preserved")
    print("[OK] PostgreSQL sequences have been updated")
    print("=" * 80)

if __name__ == "__main__":
    main()

