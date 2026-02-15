"""
Complete Reports and Report Items Migration
Ensures date_dispatched column exists and migrates both tables properly
"""

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2

POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"
SQLITE_DB = "Delivery.db"

print("=" * 80)
print("Complete Reports Migration (Reports + Report Items)")
print("=" * 80)

# Step 1: Ensure date_dispatched column exists
print("\nStep 1: Checking/adding date_dispatched column...")
pg_conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/delivery_db")
pg_cursor = pg_conn.cursor()

pg_cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'reports' AND column_name = 'date_dispatched'
""")

if not pg_cursor.fetchone():
    print("  Adding date_dispatched column...")
    pg_cursor.execute("ALTER TABLE reports ADD COLUMN date_dispatched TEXT")
    pg_conn.commit()
    print("  [OK] Column added")
else:
    print("  [OK] Column already exists")

pg_cursor.close()
pg_conn.close()

#Step 2: Migrate reports
print("\nStep 2: Migrating reports...")
print("-" * 80)

sqlite_conn = sqlite3.connect(SQLITE_DB) 
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pg_session = SessionLocal()

# Get reports from SQLite
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM reports")
reports = cursor.fetchall()

cursor.execute("PRAGMA table_info(reports)")
report_columns = [row[1] for row in cursor.fetchall()]

print(f"Found {len(reports)} reports in SQLite")

# Clear and migrate
pg_session.execute(text("DELETE FROM report_items"))
pg_session.execute(text("DELETE FROM reports"))
pg_session.commit()

migrated = 0
for row in reports:
    params = {col: value for col, value in zip(report_columns, row)}
    column_list = ", ".join(report_columns)
    param_list = ", ".join([f":{col}" for col in report_columns])
    
    try:
        pg_session.execute(
            text(f"INSERT INTO reports ({column_list}) VALUES ({param_list})"),
            params
        )
        migrated += 1
    except Exception as e:
        print(f"  [ERROR] Failed to migrate report ID {params.get('id')}: {e}")
        pg_session.rollback()
        break

pg_session.commit()
print(f"[OK] Migrated {migrated} reports")

# Update sequence
if migrated > 0:
    max_id = pg_session.execute(text("SELECT MAX(id) FROM reports")).scalar()
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('reports', 'id'), {max_id})"))
    pg_session.commit()
    print(f"[OK] Updated reports sequence to {max_id + 1}")

# Step 3: Migrate report_items
print("\nStep 3: Migrating report_items...")
print("-" * 80)

cursor.execute("SELECT * FROM report_items")
items = cursor.fetchall()

cursor.execute("PRAGMA table_info(report_items)")
item_columns = [row[1] for row in cursor.fetchall()]

print(f"Found {len(items)} report items in SQLite")

migrated_items = 0
for i, row in enumerate(items):
    params = {col: value for col, value in zip(item_columns, row)}
    column_list = ", ".join(item_columns)
    param_list = ", ".join([f":{col}" for col in item_columns])
    
    try:
        pg_session.execute(
            text(f"INSERT INTO report_items ({column_list}) VALUES ({param_list})"),
            params
        )
        migrated_items += 1
        
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{len(items)}")
            pg_session.commit()  # Commit in batches
            
    except Exception as e:
        print(f"  [ERROR] Row {params.get('id')}: {str(e)[:100]}")
        pg_session.rollback()
        if migrated_items == 0 and i < 5:
            # Show details for first few errors
            print(f"    Params: {params}")
        break

pg_session.commit()
print(f"[OK] Migrated {migrated_items} report items")

# Update sequence
if migrated_items > 0:
    max_id = pg_session.execute(text("SELECT MAX(id) FROM report_items")).scalar()
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('report_items', 'id'), {max_id})"))
    pg_session.commit()
    print(f"[OK] Updated report_items sequence to {max_id + 1}")

sqlite_conn.close()
pg_session.close()

print("\n" + "=" * 80)
print("Migration Complete")
print("=" * 80)
print(f"Reports: {migrated}/{len(reports)}")
print(f"Report Items: {migrated_items}/{len(items)}")
print("=" * 80)
