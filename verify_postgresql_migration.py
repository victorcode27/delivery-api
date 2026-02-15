"""
PostgreSQL Migration Verification Script
Connects to delivery_db and verifies schema
"""
import psycopg2
from psycopg2 import sql

# Connection parameters
DB_URL = "postgresql://postgres:1234@localhost:5432/delivery_db"

def verify_database():
    """Verify PostgreSQL database and tables"""
    results = {
        "database_exists": False,
        "tables": {},
        "errors": []
    }
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        results["database_exists"] = True
        print("✅ Successfully connected to delivery_db\n")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Found {len(tables)} tables:\n")
        
        # Expected tables from init_db()
        expected_tables = [
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
        
        # Get row count for each table
        for table in tables:
            try:
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table)
                ))
                count = cursor.fetchone()[0]
                results["tables"][table] = count
                
                status = "✅" if table in expected_tables else "⚠️"
                print(f"{status} {table}: {count} rows")
            except Exception as e:
                results["errors"].append(f"Error counting {table}: {e}")
                print(f"❌ {table}: ERROR - {e}")
        
        print("\n" + "="*60)
        
        # Check for missing expected tables
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"\n❌ Missing expected tables: {', '.join(missing_tables)}")
            results["errors"].append(f"Missing tables: {missing_tables}")
        else:
            print("\n✅ All expected tables exist!")
        
        # Check for extra tables (not critical)
        extra_tables = set(tables) - set(expected_tables)
        if extra_tables:
            print(f"\n⚠️  Extra tables found: {', '.join(extra_tables)}")
        
        cursor.close()
        conn.close()
        
        return results
        
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print(f"❌ Database 'delivery_db' does not exist")
            results["errors"].append("Database does not exist")
        else:
            print(f"❌ Connection error: {e}")
            results["errors"].append(f"Connection error: {e}")
        return results
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        results["errors"].append(f"Unexpected error: {e}")
        return results

if __name__ == "__main__":
    print("="*60)
    print("PostgreSQL Migration Verification")
    print("="*60)
    print(f"Connecting to: postgresql://postgres:****@localhost:5432/delivery_db\n")
    
    results = verify_database()
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"Database exists: {results['database_exists']}")
    print(f"Tables found: {len(results['tables'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
