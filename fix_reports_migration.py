"""
Fix reports table schema and re-migrate reports and report_items
"""

import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sqlite3

POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"
SQLITE_DB = "Delivery.db"

# Check and add date_dispatched column if missing
pg_conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/delivery_db")
pg_cursor = pg_conn.cursor()

print("Checking reports table schema...")
pg_cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'reports' AND column_name = 'date_dispatched'
""")

if not pg_cursor.fetchone():
    print("Adding missing date_dispatched column...")
    pg_cursor.execute("ALTER TABLE reports ADD COLUMN date_dispatched TEXT")
    pg_conn.commit()
    print("[OK] Added date_dispatched column")
else:
    print("[OK] date_dispatched column already exists")

pg_cursor.close()
pg_conn.close()

# Now migrate reports and report_items
print("\nMigrating reports table...")
sqlite_conn = sqlite3.connect(SQLITE_DB)
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pg_session = SessionLocal()

# Clear existing reports data
pg_session.execute(text("DELETE FROM report_items"))
pg_session.execute(text("DELETE FROM reports"))
pg_session.commit()

# Get reports from SQLite
cursor = sqlite_conn.cursor()

cursor.execute("SELECT * FROM reports")
reports = cursor.fetchall()

cursor.execute("PRAGMA table_info(reports)")
report_columns = [row[1] for row in cursor.fetchall()]

print(f"Found {len(reports)} reports to migrate")

# Insert reports
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
        print(f"Error: {e}")
        print(f"Params: {params}")
        break

pg_session.commit()
print(f"[OK] Migrated {migrated} reports")

# Update sequence
max_id = pg_session.execute(text("SELECT MAX(id) FROM reports")).scalar()
if max_id:
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('reports', 'id'), {max_id})"))
    pg_session.commit()
    print(f"[OK] Updated reports sequence to {max_id + 1}")

# Migrate report_items
print("\nMigrating report_items table...")
cursor.execute("SELECT * FROM report_items")
items = cursor.fetchall()

cursor.execute("PRAGMA table_info(report_items)")
item_columns = [row[1] for row in cursor.fetchall()]

print(f"Found {len(items)} report items to migrate")

migrated = 0
for row in items:
    params = {col: value for col, value in zip(item_columns, row)}
    column_list = ", ".join(item_columns)
    param_list = ", ".join([f":{col}" for col in item_columns])
    
    try:
        pg_session.execute(
            text(f"INSERT INTO report_items ({column_list}) VALUES ({param_list})"),
            params
        )
        migrated += 1
    except Exception as e:
        print(f"Error on row {migrated}: {e}")
        if migrated > 5:
            break

pg_session.commit()
print(f"[OK] Migrated {migrated} report items")

# Update sequence
max_id = pg_session.execute(text("SELECT MAX(id) FROM report_items")).scalar()
if max_id:
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('report_items', 'id'), {max_id})"))
    pg_session.commit()
    print(f"[OK] Updated report_items sequence to {max_id + 1}")

sqlite_conn.close()
pg_session.close()

print("\n[SUCCESS] Reports and report_items migration complete!")
