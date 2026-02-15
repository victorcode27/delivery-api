"""
Final migration - handle duplicates and complete migration
"""

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"
SQLITE_DB = "Delivery.db"

print("=" * 80)
print("Final Reports Migration")
print("=" * 80)

sqlite_conn = sqlite3.connect(SQLITE_DB)
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pg_session = SessionLocal()

# Get SQLite reports
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM reports")
reports = cursor.fetchall()

cursor.execute("PRAGMA table_info(reports)")
report_columns = [row[1] for row in cursor.fetchall()]

# Get existing manifest numbers in PostgreSQL
existing = pg_session.execute(text("SELECT manifest_number FROM reports")).fetchall()
existing_manifests = {row[0] for row in existing}

print(f"SQLite has {len(reports)} reports")
print(f"PostgreSQL has {len(existing_manifests)} reports")
print(f"Need to migrate {len(reports) - len(existing_manifests)} new reports\n")

# Migrate remaining reports (skip duplicates)
migrated = 0
skipped = 0

for row in reports:
    params = {col: value for col, value in zip(report_columns, row)}
    
    if params['manifest_number'] in existing_manifests:
        skipped += 1
        continue
    
    column_list = ", ".join(report_columns)
    param_list = ", ".join([f":{col}" for col in report_columns])
    
    try:
        pg_session.execute(
            text(f"INSERT INTO reports ({column_list}) VALUES ({param_list})"),
            params
        )
        migrated += 1
        existing_manifests.add(params['manifest_number'])
    except Exception as e:
        print(f"  [ERROR] Report ID {params.get('id')}: {str(e)[:100]}")

pg_session.commit()
print(f"[OK] Migrated {migrated} new reports (skipped {skipped} duplicates)")

# Update sequence
result = pg_session.execute(text("SELECT MAX(id) FROM reports")).scalar()
if result:
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('reports', 'id'), :max_id)"), {'max_id': result})
    pg_session.commit()
    print(f"[OK] Updated reports sequence to {result + 1}")

# Now migrate report_items
print("\nMigrating report_items...")
cursor.execute("SELECT * FROM report_items")
items = cursor.fetchall()

cursor.execute("PRAGMA table_info(report_items)")
item_columns = [row[1] for row in cursor.fetchall()]

# Get existing report IDs in PostgreSQL
pg_report_ids = pg_session.execute(text("SELECT id FROM reports")).fetchall()
valid_report_ids = {row[0] for row in pg_report_ids}

print(f"Found {len(items)} report items to migrate")
print(f"Valid report IDs in PostgreSQL: {len(valid_report_ids)}")

migrated_items = 0
skipped_items = 0

for i, row in enumerate(items):
    params = {col: value for col, value in zip(item_columns, row)}
    
    # Skip if report_id doesn't exist in PostgreSQL
    if params['report_id'] not in valid_report_ids:
        skipped_items += 1
        continue
    
    column_list = ", ".join(item_columns)
    param_list = ", ".join([f":{col}" for col in item_columns])
    
    try:
        pg_session.execute(
            text(f"INSERT INTO report_items ({column_list}) VALUES ({param_list})"),
            params
        )
        migrated_items += 1
        
        if (i + 1) % 100 == 0:
            pg_session.commit()
            print(f"  Progress: {migrated_items} migrated, {skipped_items} skipped")
    except Exception as e:
        print(f"  [ERROR] Item ID {params.get('id')}: {str(e)[:80]}")

pg_session.commit()
print(f"[OK] Migrated {migrated_items} report items (skipped {skipped_items})")

# Update sequence
result = pg_session.execute(text("SELECT MAX(id) FROM report_items")).scalar()
if result:
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('report_items', 'id'), :max_id)"), {'max_id': result})
    pg_session.commit()
    print(f"[OK] Updated report_items sequence to {result + 1}")

sqlite_conn.close()
pg_session.close()

print("\n" + "=" * 80)
print("Migration Complete!")
print("=" * 80)
