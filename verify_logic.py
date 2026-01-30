
import database
import invoice_processor
import os
import time

def clean_test_data():
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE filename LIKE 'TEST_%'")
    cursor.execute("DELETE FROM orders WHERE invoice_number LIKE 'BINV_TEST_%'")
    conn.commit()
    conn.close()
    print("Cleaned up old test data.")

def run_tests():
    print("--- Running Logic Verification ---")
    database.init_db()
    clean_test_data()

    # 1. Add Base Invoices
    inv1 = {
        "filename": "TEST_INV_01.pdf",
        "date_processed": "2026-01-25 10:00:00",
        "customer_name": "Client A",
        "total_value": "100.00",
        "invoice_number": "BINV_TEST_01",
        "order_number": "ORD01",
        "invoice_date": "2026-01-25",
        "area": "Area 1",
        "type": "INVOICE",
        "reference_number": None,
        "status": "PENDING"
    }
    
    inv2 = {
        "filename": "TEST_INV_02.pdf",
        "date_processed": "2026-01-25 10:00:00",
        "customer_name": "Client B",
        "total_value": "200.00",
        "invoice_number": "BINV_TEST_02",
        "order_number": "ORD02",
        "invoice_date": "2026-01-25",
        "area": "Area 2",
        "type": "INVOICE",
        "reference_number": None,
        "status": "PENDING"
    }

    print("Processing Base Invoices...")
    invoice_processor.process_invoice_logic(inv1)
    invoice_processor.process_invoice_logic(inv2)

    # Verify Base State
    o1 = database.get_order_by_invoice_number("BINV_TEST_01")
    o2 = database.get_order_by_invoice_number("BINV_TEST_02")
    if o1 and o1['total_value'] == '100.00' and o1['status'] == 'PENDING':
        print("[PASS] BINV_TEST_01 created correctly.")
    else:
        print(f"[FAIL] BINV_TEST_01 state incorrect: {o1}")

    if o2 and o2['total_value'] == '200.00' and o2['status'] == 'PENDING':
        print("[PASS] BINV_TEST_02 created correctly.")
    else:
        print(f"[FAIL] BINV_TEST_02 state incorrect: {o2}")

    # 2. Process Full Credit Note for INV 01
    cn1 = {
        "filename": "TEST_CN_01.pdf",
        "date_processed": "2026-01-25 10:05:00",
        "customer_name": "Client A",
        "total_value": "100.00",
        "invoice_number": "BCRN_TEST_01",
        "order_number": "N/A",
        "invoice_date": "2026-01-25",
        "area": "Area 1",
        "type": "CREDIT_NOTE",
        "reference_number": "BINV_TEST_01",
        "status": "PENDING"
    }
    
    print("Processing Full Credit Note...")
    invoice_processor.process_invoice_logic(cn1)
    
    # Verify Cancellation
    # Note: get_order_by_invoice_number filters by type='INVOICE', so we use it to check the Invoice
    o1_updated = database.get_order_by_invoice_number("BINV_TEST_01")
    # Actually wait, get_order_by_invoice_number does NOT filter by status, but cancelled IS a status.
    if o1_updated and o1_updated['status'] == 'CANCELLED':
        print("[PASS] BINV_TEST_01 was CANCELLED.")
    else:
        print(f"[FAIL] BINV_TEST_01 not cancelled. Status: {o1_updated.get('status')}")

    # 3. Process Partial Credit Note for INV 02 (50.00 credit)
    cn2 = {
        "filename": "TEST_CN_02.pdf",
        "date_processed": "2026-01-25 10:05:00",
        "customer_name": "Client B",
        "total_value": "50.00",
        "invoice_number": "BCRN_TEST_02",
        "order_number": "N/A",
        "invoice_date": "2026-01-25",
        "area": "Area 2",
        "type": "CREDIT_NOTE",
        "reference_number": "BINV_TEST_02",
        "status": "PENDING"
    }

    print("Processing Partial Credit Note...")
    invoice_processor.process_invoice_logic(cn2)

    # Verify Adjustment
    o2_updated = database.get_order_by_invoice_number("BINV_TEST_02")
    if o2_updated and float(o2_updated['total_value']) == 150.00 and o2_updated['status'] == 'PENDING':
        print("[PASS] BINV_TEST_02 adjusted to 150.00.")
    else:
        print(f"[FAIL] BINV_TEST_02 adjustment incorrect. Value: {o2_updated.get('total_value')}")

    # Clean up at the end? Maybe keep for inspection.
    # clean_test_data()

if __name__ == "__main__":
    run_tests()
