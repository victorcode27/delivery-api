"""
Check what reports actually made it to PostgreSQL
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pg_session = SessionLocal()

# Check reports
count = pg_session.execute(text("SELECT COUNT(*) FROM reports")).scalar()
print(f"Reports in PostgreSQL: {count}")

if count > 0:
    print("\nFirst 5 report IDs:")
    ids = pg_session.execute(text("SELECT id, manifest_number FROM reports ORDER BY id LIMIT 5")).fetchall()
    for row in ids:
        print(f"  ID {row[0]}: {row[1]}")
else:
    print("No reports found!")

pg_session.close()
