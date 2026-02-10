"""
Database module for the Delivery Manifest System.
Uses SQLite for persistent, corruption-resistant storage.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

# Database file path (same directory as this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "delivery.db")

def get_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Orders table - stores invoice/order data
    # Added type, reference_number, original_value, status for Credit Note support
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            date_processed TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            total_value TEXT DEFAULT '0.00',
            order_number TEXT DEFAULT 'N/A',
            invoice_number TEXT DEFAULT 'N/A',
            invoice_date TEXT DEFAULT 'N/A',
            area TEXT DEFAULT 'UNKNOWN',
            is_allocated INTEGER DEFAULT 0,
            allocated_date TEXT,
            manifest_number TEXT,
            manifest_number TEXT,
            type TEXT DEFAULT 'INVOICE',
            reference_number TEXT,
            original_value TEXT,
            status TEXT DEFAULT 'PENDING',
            customer_number TEXT DEFAULT 'N/A'  -- Added Customer Number
        )
    ''')
    
    # Check if we need to migrate existing table (add new columns if missing)
    try:
        cursor.execute("SELECT customer_number FROM orders LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating database: Adding customer_number column...")
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN customer_number TEXT DEFAULT 'N/A'")
        except Exception as e:
            print(f"Migration warning: {e}")

    # Users table... (rest remains same)
    
    # Reports table... (rest remains same)

    # Report items table - links invoices to reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            invoice_number TEXT NOT NULL,
            order_number TEXT,
            customer_name TEXT,
            customer_number TEXT,  -- Added Customer Number
            invoice_date TEXT,
            area TEXT,
            sku INTEGER DEFAULT 0,
            value REAL DEFAULT 0,
            weight REAL DEFAULT 0,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        )
    ''')
    
    # Add migration for report_items too
    try:
        cursor.execute("SELECT customer_number FROM report_items LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating database: Adding customer_number to report_items...")
        try:
            cursor.execute("ALTER TABLE report_items ADD COLUMN customer_number TEXT DEFAULT 'N/A'")
        except Exception as e:
            print(f"Migration warning (report_items): {e}")
    
    # Settings table - stores app settings (routes, drivers, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            value TEXT NOT NULL,
            UNIQUE(category, value)
        )
    ''')
    
    # Trucks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trucks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg TEXT UNIQUE NOT NULL,
            driver TEXT,
            assistant TEXT,
            checker TEXT
        )
    ''')

    # Customer Routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT UNIQUE NOT NULL,
            route_name TEXT NOT NULL
        )
    ''')

    # Manifest Events table (Audit Trail)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manifest_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manifest_number TEXT NOT NULL,
            event_type TEXT NOT NULL,
            performed_by TEXT DEFAULT 'System',
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Manifest Staging table (FIX: Prevents invoices from disappearing)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manifest_staging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            invoice_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES orders(id)
        )
    ''')
    
    # Create index for faster staging queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_staging_session 
        ON manifest_staging(session_id)
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")
    
    # Check if we need to create a default admin user
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT count(*) FROM users')
    if c.fetchone()[0] == 0:
        pass_hash = hashlib.sha256("admin".encode()).hexdigest()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO users (username, password_hash, is_admin, can_manifest, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', pass_hash, 1, 1, now))
        conn.commit()
        print("Created default admin user (admin/admin)")
    conn.close()

# =============================================
# ORDER FUNCTIONS
# =============================================

def get_all_orders(allocated: bool = False) -> List[Dict]:
    """Get all orders. If allocated=False, only return pending orders."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Modified to only show INVOICE type in the main lists and filter by status
    if allocated:
        # Show allocated invoices
        cursor.execute("SELECT * FROM orders WHERE type = 'INVOICE' ORDER BY date_processed DESC")
    else:
        # Show pending invoices (not allocated and not cancelled)
        cursor.execute("SELECT * FROM orders WHERE is_allocated = 0 AND type = 'INVOICE' AND status != 'CANCELLED' ORDER BY date_processed DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts matching the old JSON format
    return [dict(row) for row in rows]

def get_order_by_filename(filename: str) -> Optional[Dict]:
    """Get a single order by filename."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE filename = ?', (filename,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
    
def get_order_by_invoice_number(invoice_number: str) -> Optional[Dict]:
    """Get a single order by invoice number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE invoice_number = ? AND type = 'INVOICE'", (invoice_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_order_value(invoice_number: str, new_value: str, original_value: str = None) -> bool:
    """Update the value of an order (used for Partial Credit)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if original_value:
             cursor.execute("UPDATE orders SET total_value = ?, original_value = ? WHERE invoice_number = ?", 
                           (new_value, original_value, invoice_number))
        else:
             cursor.execute("UPDATE orders SET total_value = ? WHERE invoice_number = ?", 
                           (new_value, invoice_number))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    except Exception as e:
        print(f"Error updating order value: {e}")
        conn.close()
        return False

def cancel_order(invoice_number: str) -> bool:
    """Mark an order as CANCELLED (used for Full Credit)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status = 'CANCELLED' WHERE invoice_number = ?", (invoice_number,))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    except Exception as e:
        print(f"Error cancelling order: {e}")
        conn.close()
        return False

def add_order(order_data: Dict) -> bool:
    """Add a new order/credit note to the database. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO orders (filename, date_processed, customer_name, total_value, 
                              order_number, invoice_number, invoice_date, area,
                              type, reference_number, original_value, status, customer_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data.get('filename'),
            order_data.get('date_processed', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            order_data.get('customer_name', 'Unknown'),
            order_data.get('total_value', '0.00'),
            order_data.get('order_number', 'N/A'),
            order_data.get('invoice_number', 'N/A'),
            order_data.get('invoice_date', 'N/A'),
            order_data.get('area', 'UNKNOWN'),
            order_data.get('type', 'INVOICE'),
            order_data.get('reference_number', None),
            order_data.get('original_value', None),
            order_data.get('status', 'PENDING'),
            order_data.get('customer_number', 'N/A')
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Duplicate filename
        conn.close()
        return False

def allocate_orders(filenames: List[str], manifest_number: str = None) -> int:
    """Mark orders as allocated. Returns count of updated orders."""
    conn = get_connection()
    cursor = conn.cursor()
    
    allocated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    placeholders = ','.join(['?' for _ in filenames])
    
    cursor.execute(f'''
        UPDATE orders 
        SET is_allocated = 1, allocated_date = ?, manifest_number = ?
        WHERE filename IN ({placeholders})
    ''', [allocated_date, manifest_number] + filenames)
    
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated

def get_areas() -> List[str]:
    """Get unique areas from all orders."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT area FROM orders WHERE area != "UNKNOWN" ORDER BY area')
    rows = cursor.fetchall()
    conn.close()
    return [row['area'] for row in rows]

def get_all_customers() -> List[str]:
    """Get unique customer names from all orders (pending and allocated)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT customer_name FROM orders ORDER BY customer_name')
    rows = cursor.fetchall()
    conn.close()
    return [row['customer_name'] for row in rows]

def search_orders(query: str) -> List[Dict]:
    """Search for orders (pending or allocated) by invoice, order #, or customer."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # We want to match partial strings
    like_query = f"%{query}%"
    
    cursor.execute('''
        SELECT * FROM orders 
        WHERE invoice_number LIKE ? 
            OR order_number LIKE ? 
            OR customer_name LIKE ?
            OR filename LIKE ?
            OR customer_number LIKE ?
        ORDER BY date_processed DESC
        LIMIT 50
    ''', (like_query, like_query, like_query, like_query, like_query))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def deallocate_orders(filenames: List[str]) -> int:
    """Reset orders to pending status (un-allocate). Returns count of updated orders."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if not filenames:
        return 0

    placeholders = ','.join(['?' for _ in filenames])
    
    cursor.execute(f'''
        UPDATE orders 
        SET is_allocated = 0, allocated_date = NULL, manifest_number = NULL
        WHERE filename IN ({placeholders})
    ''', filenames)
    
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated

def get_available_orders_excluding_staging():
    """Return orders not allocated and not present in manifest staging."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM orders o
        WHERE o.id NOT IN (
            SELECT invoice_id FROM manifest_staging
        )
        AND o.type = 'INVOICE'
        AND (
            o.manifest_number IS NULL
            OR o.manifest_number NOT IN (
                SELECT DISTINCT manifest_number FROM reports
            )
        )
        ORDER BY o.date_processed DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# =============================================
# MANIFEST STAGING FUNCTIONS (FIX FOR WORKFLOW BUG)
# =============================================

def add_to_staging(session_id: str, filenames: List[str]) -> int:
    """Add invoices to manifest staging. Invoices remain AVAILABLE until confirmed. Returns count added."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if not filenames or not session_id:
        return 0
    
    # Get invoice IDs from filenames
    placeholders = ','.join(['?' for _ in filenames])
    cursor.execute(f'''
        SELECT id, filename FROM orders 
        WHERE filename IN ({placeholders})
    ''', filenames)
    
    invoice_rows = cursor.fetchall()
    added_count = 0
    
    for row in invoice_rows:
        invoice_id = row['id']
        # Check if already in staging for this session
        cursor.execute('''
            SELECT id FROM manifest_staging 
            WHERE session_id = ? AND invoice_id = ?
        ''', (session_id, invoice_id))
        
        if cursor.fetchone() is None:
            # Not in staging, add it
            cursor.execute('''
                INSERT INTO manifest_staging (session_id, invoice_id)
                VALUES (?, ?)
            ''', (session_id, invoice_id))
            added_count += 1
    
    conn.commit()
    conn.close()
    return added_count

def get_current_manifest(session_id: str, manifest_number: str = None) -> List[Dict]:
    """Get all invoices for the current manifest.
    
    Returns:
    - Finalized invoices (orders.manifest_number = manifest_number AND is_allocated=1)
    - Plus in-progress staging entries for this session (that aren't already finalized)
    - Only type='INVOICE' rows, no duplicates
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if manifest_number:
        # Return finalized invoices for this manifest UNION with NEW staging entries only
        cursor.execute('''
            SELECT o.* FROM orders o
            WHERE o.manifest_number = ? AND o.is_allocated = 1 AND o.type = 'INVOICE'
            UNION
            SELECT o.* FROM orders o
            INNER JOIN manifest_staging ms ON ms.invoice_id = o.id
            WHERE ms.session_id = ? 
            AND o.type = 'INVOICE'
            AND o.is_allocated = 0
            AND (o.manifest_number IS NULL OR o.manifest_number != ?)
            ORDER BY date_processed DESC
        ''', (manifest_number, session_id, manifest_number))
    else:
        # Staging only (backward compatible) - exclude already allocated
        cursor.execute('''
            SELECT o.* 
            FROM orders o
            INNER JOIN manifest_staging ms ON ms.invoice_id = o.id
            WHERE ms.session_id = ? 
            AND o.type = 'INVOICE'
            AND o.is_allocated = 0
            ORDER BY ms.added_at ASC
        ''', (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def remove_from_staging(session_id: str, filenames: List[str]) -> int:
    """Remove invoices from manifest staging. Makes them instantly available again. Returns count removed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if not filenames or not session_id:
        return 0
    
    # Get invoice IDs from filenames
    placeholders = ','.join(['?' for _ in filenames])
    cursor.execute(f'''
        SELECT id FROM orders 
        WHERE filename IN ({placeholders})
    ''', filenames)
    
    invoice_ids = [row['id'] for row in cursor.fetchall()]
    
    if not invoice_ids:
        conn.close()
        return 0
    
    # Delete from staging
    id_placeholders = ','.join(['?' for _ in invoice_ids])
    cursor.execute(f'''
        DELETE FROM manifest_staging
        WHERE session_id = ? AND invoice_id IN ({id_placeholders})
    ''', [session_id] + invoice_ids)
    
    removed = cursor.rowcount
    
    # FIX: Clear allocation flags for removed invoices
    # BUT ONLY if they're not in finalized reports (to preserve dispatch history)
    cursor.execute(f'''
        UPDATE orders
        SET is_allocated = 0, allocated_date = NULL, manifest_number = NULL
        WHERE id IN ({id_placeholders})
        AND (manifest_number IS NULL OR manifest_number NOT IN (
            SELECT DISTINCT manifest_number FROM reports
        ))
    ''', invoice_ids)
    
    conn.commit()
    conn.close()
    return removed

def clear_staging(session_id: str) -> int:
    """Clear all staging entries for a session. Returns count cleared."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM manifest_staging WHERE session_id = ?', (session_id,))
    cleared = cursor.rowcount
    
    conn.commit()
    conn.close()
    return cleared

# =============================================
# USER FUNCTIONS
# =============================================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username: str) -> Optional[Dict]:
    """Get a user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username: str, password: str, is_admin: bool = False, can_manifest: bool = True) -> bool:
    """Create a new user. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, can_manifest, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            hash_password(password),
            1 if is_admin else 0,
            1 if can_manifest else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials. Returns user dict if valid, None otherwise."""
    user = get_user(username)
    if user and user['password_hash'] == hash_password(password):
        return user
    return None

def get_all_users() -> List[Dict]:
    """Get all users (without password hashes)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, is_admin, can_manifest, created_at FROM users')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user(username: str) -> bool:
    """Delete a user by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_user(username: str, password: str = None, is_admin: bool = None, can_manifest: bool = None) -> bool:
    """Update user details."""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if password is not None:
        updates.append('password_hash = ?')
        params.append(hash_password(password))
    if is_admin is not None:
        updates.append('is_admin = ?')
        params.append(1 if is_admin else 0)
    if can_manifest is not None:
        updates.append('can_manifest = ?')
        params.append(1 if can_manifest else 0)
    
    if not updates:
        conn.close()
        return False
    
    params.append(username)
    cursor.execute(f'UPDATE users SET {", ".join(updates)} WHERE username = ?', params)
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

# =============================================
# REPORT FUNCTIONS
# =============================================

def save_report(report_data: Dict) -> int:
    """Save a dispatch report. Returns the report ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reports (manifest_number, date, date_dispatched, driver, assistant, checker, reg_number,
                            pallets_brown, pallets_blue, crates, mileage, total_value, 
                            total_sku, total_weight, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report_data.get('manifestNumber'),
        report_data.get('date'),
        report_data.get('date'),  # date_dispatched = date
        report_data.get('driver'),
        report_data.get('assistant'),
        report_data.get('checker'),
        report_data.get('regNumber'),
        report_data.get('palletsBrown', 0),
        report_data.get('palletsBlue', 0),
        report_data.get('crates', 0),
        report_data.get('mileage', 0),
        report_data.get('totalValue', 0),
        report_data.get('totalSku', 0),
        report_data.get('totalWeight', 0),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    report_id = cursor.lastrowid
    
    # Save report items (invoices)
    for invoice in report_data.get('invoices', []):
        cursor.execute('''
            INSERT INTO report_items (report_id, invoice_number, order_number, customer_name,
                                        invoice_date, area, sku, value, weight, customer_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_id,
            invoice.get('num') or invoice.get('invoice_number', 'N/A'),
            invoice.get('orderNum') or invoice.get('order_number', 'N/A'),
            invoice.get('customer') or invoice.get('customer_name', 'N/A'),
            invoice.get('invoiceDate') or invoice.get('invoice_date', 'N/A'),
            invoice.get('area', 'UNKNOWN'),
            invoice.get('sku', 0),
            invoice.get('value', 0) or invoice.get('total_value', 0),
            invoice.get('weight', 0),
            invoice.get('customerNumber') or invoice.get('customer_number', 'N/A')
        ))
    
    # FIX: Finalize invoices from staging if session_id is provided
    session_id = report_data.get('session_id')
    if session_id:
        # Get all invoice filenames from staging for this session
        cursor.execute('''
            SELECT o.filename
            FROM orders o
            INNER JOIN manifest_staging ms ON ms.invoice_id = o.id
            WHERE ms.session_id = ?
        ''', (session_id,))
        
        staged_filenames = [row['filename'] for row in cursor.fetchall()]
        
        if staged_filenames:
            # Update invoices to DISPATCHED
            placeholders = ','.join(['?' for _ in staged_filenames])
            allocated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f'''
                UPDATE orders
                SET is_allocated = 1, allocated_date = ?, manifest_number = ?
                WHERE filename IN ({placeholders})
            ''', [allocated_date, report_data.get('manifestNumber')] + staged_filenames)
            
            print(f"Finalized {cursor.rowcount} invoices from staging for session: {session_id}")
        
        # Clear staging for this session
        cursor.execute('DELETE FROM manifest_staging WHERE session_id = ?', (session_id,))
        print(f"Cleared staging for session: {session_id}")
    
    conn.commit()
    conn.close()

    # Log the event
    log_manifest_event(report_data.get('manifestNumber'), 'CREATED', 'System')

    return report_id

def get_reports(date_from: str = None, date_to: str = None) -> List[Dict]:
    """Get all reports with their items, optionally filtered by date range."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM reports'
    params = []
    
    if date_from or date_to:
        conditions = []
        if date_from:
            conditions.append('date >= ?')
            params.append(date_from)
        if date_to:
            conditions.append('date <= ?')
            # Extend date_to to end of day to include all dispatches on that date
            params.append(date_to + " 23:59:59")
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY id DESC'
    cursor.execute(query, params)
    reports = [dict(row) for row in cursor.fetchall()]
    
    # Add items to each report
    for report in reports:
        cursor.execute('SELECT * FROM report_items WHERE report_id = ?', (report['id'],))
        report['invoices'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return reports

def get_manifest_details(manifest_number: str) -> Optional[Dict]:
    """Get full details of a specific manifest including invoices and events."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get Report Metadata
    cursor.execute('SELECT * FROM reports WHERE manifest_number = ?', (manifest_number,))
    report = cursor.fetchone()
    
    if not report:
        conn.close()
        return None
        
    result = dict(report)
    
    # Get Linked Invoices
    cursor.execute('SELECT * FROM report_items WHERE report_id = ?', (result['id'],))
    result['invoices'] = [dict(row) for row in cursor.fetchall()]
    
    # Get Audit Events
    cursor.execute('SELECT * FROM manifest_events WHERE manifest_number = ? ORDER BY timestamp DESC', (manifest_number,))
    result['events'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return result

def log_manifest_event(manifest_number: str, event_type: str, performed_by: str = 'System') -> bool:
    """Log an event for a manifest."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO manifest_events (manifest_number, event_type, performed_by, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (manifest_number, event_type, performed_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging event: {e}")
        conn.close()
        return False

# =============================================
# SETTINGS FUNCTIONS
# =============================================

def get_settings(category: str) -> List[str]:
    """Get all values for a settings category (drivers, assistants, checkers, routes)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE category = ? ORDER BY value', (category,))
    rows = cursor.fetchall()
    conn.close()
    return [row['value'] for row in rows]

def add_setting(category: str, value: str) -> bool:
    """Add a setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO settings (category, value) VALUES (?, ?)', (category, value))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_setting(category: str, value: str) -> bool:
    """Delete a setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM settings WHERE category = ? AND value = ?', (category, value))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_setting(category: str, old_value: str, new_value: str) -> bool:
    """Update a setting value."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE settings SET value = ? WHERE category = ? AND value = ?', 
                      (new_value, category, old_value))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    except sqlite3.IntegrityError:
        conn.close()
        return False

# =============================================
# TRUCK FUNCTIONS
# =============================================

def get_trucks() -> List[Dict]:
    """Get all trucks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trucks ORDER BY reg')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_truck(reg: str, driver: str = None, assistant: str = None, checker: str = None) -> bool:
    """Add a truck."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO trucks (reg, driver, assistant, checker) VALUES (?, ?, ?, ?)',
                      (reg, driver, assistant, checker))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_truck(reg: str) -> bool:
    """Delete a truck by registration."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trucks WHERE reg = ?', (reg,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_truck(reg: str, driver: str = None, assistant: str = None, checker: str = None) -> bool:
    """Update truck details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE trucks SET driver = ?, assistant = ?, checker = ? WHERE reg = ?',
                  (driver, assistant, checker, reg))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

# =============================================
# CUSTOMER ROUTE FUNCTIONS
# =============================================

def get_customer_routes() -> Dict[str, str]:
    """Get all customer route mappings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT customer_name, route_name FROM customer_routes')
    rows = cursor.fetchall()
    conn.close()
    return {row['customer_name']: row['route_name'] for row in rows}

def add_customer_route(customer_name: str, route_name: str) -> bool:
    """Add or update a customer route mapping."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Use REPLACE to handle updates
        cursor.execute('REPLACE INTO customer_routes (customer_name, route_name) VALUES (?, ?)', 
                      (customer_name, route_name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_customer_route(customer_name: str) -> bool:
    """Delete a customer route mapping."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customer_routes WHERE customer_name = ?', (customer_name,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# =============================================
# MIGRATION HELPER
# =============================================

def migrate_from_json(json_file_path: str) -> int:
    """Migrate existing orders from JSON file to database. Returns count of migrated orders."""
    if not os.path.exists(json_file_path):
        return 0
    
    try:
        with open(json_file_path, 'r') as f:
            orders = json.load(f)
    except (json.JSONDecodeError, IOError):
        return 0
    
    migrated = 0
    for order in orders:
        if add_order(order):
            migrated += 1
    
    return migrated


# =============================================
# NEW DISPATCH REPORT QUERIES
# =============================================

def get_dispatched_invoices(
    date_from: str = None,
    date_to: str = None,
    filter_type: str = "dispatch",  # NEW: 'dispatch' or 'manifest'
    search_query: str = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "date_dispatched",
    sort_order: str = "DESC"
) -> tuple:
    """
    Get dispatched invoices as INVOICE-LEVEL ROWS (one row per invoice).
    
    Each row includes denormalized dispatch metadata + invoice snapshot.
    
    Args:
        date_from: Filter by date >= this value (YYYY-MM-DD)
        date_to: Filter by date <= this value (YYYY-MM-DD)
        filter_type: 'dispatch' (filter by r.date_dispatched) or 'manifest' (filter by manifest creation)
        search_query: Global text search across invoice #, order #, manifest #, customer, driver, truck reg, checker
        limit: Maximum number of results to return (pagination)
        offset: Number of results to skip (pagination)
        sort_by: Field to sort by (default: date_dispatched)
        sort_order: Sort order ASC or DESC (default: DESC)
    
    Returns:
        Tuple of (results list, total count after filters)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Base query - JOIN reports and report_items to get invoice-level rows
    query = """
        SELECT 
            r.manifest_number,
            r.date_dispatched,
            r.driver,
            r.assistant,
            r.checker,
            r.reg_number,
            ri.invoice_number,
            ri.order_number,
            ri.customer_name,
            ri.customer_number,
            ri.invoice_date,
            ri.area,
            ri.sku,
            ri.value,
            ri.weight
        FROM reports r
        INNER JOIN report_items ri ON r.id = ri.report_id
    """
    
    where_clauses = []
    params = []
    
    # Date range filtering based on filter_type
    # NOTE: Currently both modes use r.date_dispatched because we don't have
    # a timestamp on report_items. This can be enhanced later.
    if filter_type == "manifest":
        # Future enhancement: filter by report_items.created_at when that column exists
        # For now, use same logic as dispatch mode
        if date_from:
            where_clauses.append("r.date_dispatched >= ?")
            params.append(date_from)
        
        if date_to:
            where_clauses.append("r.date_dispatched <= ?")
            params.append(date_to)
    else:  # dispatch mode (default)
        if date_from:
            where_clauses.append("r.date_dispatched >= ?")
            params.append(date_from)
        
        if date_to:
            where_clauses.append("r.date_dispatched <= ?")
            params.append(date_to)
    
    # Global text search
    if search_query:
        search_pattern = f"%{search_query}%"
        where_clauses.append("""(
            ri.invoice_number LIKE ? OR
            ri.order_number LIKE ? OR
            r.manifest_number LIKE ? OR
            ri.customer_name LIKE ? OR
            r.driver LIKE ? OR
            r.reg_number LIKE ? OR
            r.checker LIKE ?
        )""")
        # Add the search pattern 7 times for each field
        params.extend([search_pattern] * 7)
    
    # Add WHERE clause if any filters
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Get total count (before pagination)
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    
    # Add sorting
    valid_sort_fields = {
        "date_dispatched": "r.date_dispatched",
        "manifest_number": "r.manifest_number",
        "invoice_number": "ri.invoice_number",
        "customer_name": "ri.customer_name",
        "driver": "r.driver"
    }
    
    sort_field = valid_sort_fields.get(sort_by, "r.date_dispatched")
    sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"
    query += f" ORDER BY {sort_field} {sort_order}"
    
    # Add pagination
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    # Execute query
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    results = []
    for row in rows:
        results.append({
            "manifest_number": row[0],
            "date_dispatched": row[1],
            "driver": row[2],
            "assistant": row[3],
            "checker": row[4],
            "reg_number": row[5],
            "invoice_number": row[6],
            "order_number": row[7],
            "customer_name": row[8],
            "customer_number": row[9],
            "invoice_date": row[10],
            "area": row[11],
            "sku": row[12],
            "value": row[13],
            "weight": row[14]
        })
    
    return (results, total_count)


def get_outstanding_orders() -> List[Dict]:
    """
    Get outstanding orders (invoices with NO dispatch record).
    
    CRITICAL: This checks if invoice_number exists in report_items table,
    NOT the is_allocated flag. This ensures we get truly un-dispatched invoices.
    
    Excludes cancelled invoices.
    
    Returns:
        List of outstanding orders with: invoice_number, order_number, customer_name, invoice_date
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            invoice_number,
            order_number,
            customer_name,
            invoice_date,
            customer_number,
            total_value,
            area
        FROM orders
        WHERE 
            invoice_number NOT IN (SELECT DISTINCT invoice_number FROM report_items)
            AND status != 'CANCELLED'
            AND type = 'INVOICE'
        ORDER BY invoice_date DESC, invoice_number DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    results = []
    for row in rows:
        results.append({
            "invoice_number": row[0],
            "order_number": row[1],
            "customer_name": row[2],
            "invoice_date": row[3],
            "customer_number": row[4],
            "total_value": row[5],
            "area": row[6]
        })
    
    return results


# Initialize DB when module is imported
if __name__ == "__main__":
    init_db()
    # Create default admin user if no users exist
    if not get_all_users():
        create_user('admin', 'admin', is_admin=True, can_manifest=True)
        print("Created default admin user (admin/admin)")
