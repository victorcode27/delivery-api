"""
Complete migration for report_items with proper error handling
"""

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"
SQLITE_DB = "Delivery.db"

print("=" * 80)
print("Report Items Migration")
print("=" * 80)

# Connect
sqlite_conn = sqlite3.connect(SQLITE_DB)
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pg_session = SessionLocal()

# Clear existing report_items
print("\nClearing existing report_items...")
pg_session.execute(text("DELETE FROM report_items"))
pg_session.commit()
print("[OK] Cleared report_items")

# Get data from SQLite
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM report_items")
items = cursor.fetchall()

cursor.execute("PRAGMA table_info(report_items)")
columns = [row[1] for row in cursor.fetchall()]

print(f"\nMigrating {len(items)} report items...")
print("-" * 80)

# Migrate one by one with individual transactions
migrated = 0
errors = []

for i, row in enumerate(items):
    try:
        params = {col: value for col, value in zip(columns, row)}
        column_list = ", ".join(columns)
        param_list = ", ".join([f":{col}" for col in columns])
        
        pg_session.execute(
            text(f"INSERT INTO report_items ({column_list}) VALUES ({param_list})"),
            params
        )
        pg_session.commit()  # Commit each row individually
        migrated += 1
        
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{len(items)} rows...")
            
    except Exception as e:
        pg_session.rollback()  # Rollback this individual insert
        error_msg = str(e).split('\n')[0]  # First line of error
        errors.append((params.get('id', 'unknown'), error_msg))
        
        if len(errors) <= 10:
            print(f"  [ERROR] Row {params.get('id')}: {error_msg}")

print()
print(f"[OK] Successfully migrated {migrated} out of {len(items)} report items")

if errors:
    print(f"[WARNING] {len(errors)} rows failed to migrate")
    if len(errors) > 10:
        print(f"  (Showing find 10 errors)")
        for row_id, error in errors[:10]:
            print(f"    Row {row_id}: {error}")
else:
    print("[OK] All rows migrated successfully!")

# Update sequence
print("\nUpdating sequence...")
max_id = pg_session.execute(text("SELECT MAX(id) FROM report_items")).scalar()
if max_id:
    pg_session.execute(text(f"SELECT setval(pg_get_serial_sequence('report_items', 'id'), {max_id})"))
    pg_session.commit()
    print(f"[OK] Sequence updated to start from {max_id + 1}")

sqlite_conn.close()
pg_session.close()

print("\n" + "=" * 80)
print("Migration Complete!")
print("=" * 80)
