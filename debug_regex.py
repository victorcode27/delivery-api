import re
import datetime

def test_logic():
    # Simulated text from a text-based PDF
    text = """
    INVOICE
    
    Customer House No: 1234 TEST CUSTOMER LTD
    Telephone: 555-0199
    
    Date: 2026-01-26
    
    Account   Date       Order No
    TEST001   26/01/2026 SO-9988-XY
    
    Description           Amount
    ----------------------------
    Widget A              $50.00
    
    Invoice Total:        $50.00
    Invoice No:           BINV_TEST_001
    """
    
    data = {"order_number": "N/A", "invoice_date": "N/A"}
    
    # Test the Order Number Regex (The one we modified)
    print("Testing Header Regex...")
    order_header_match = re.search(r"Account\s+Date\s+Order\s+No", text, re.IGNORECASE)
    if order_header_match:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "Account" in line and "Date" in line and "Order" in line:
                if i + 1 < len(lines):
                    data_line = lines[i+1]
                    print(f"Checking line: '{data_line}'")
                    # data_match = re.search(r"[\w\d]+\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d+)", data_line) # OLD
                    data_match = re.search(r"[\w\d]+\s+(\d{1,2}/\d{1,2}/\d{4})\s+([\w\d\-\.]+)", data_line) # NEW (Slightly wider)
                    
                    if data_match:
                        raw_date = data_match.group(1).strip()
                        data["invoice_date"] = raw_date
                        data["order_number"] = data_match.group(2).strip()
                        print("MATCH FOUND!")
                        break
                    else:
                        print("NO MATCH on data line")

    print(f"Result: Order='{data['order_number']}', Date='{data['invoice_date']}'")
    
    # Test Fallback Regex
    print("\nTesting Fallback Regex...")
    text_fallback = "Order No: SO-ABC-123"
    order_alt_match = re.search(r"Order\s*(?:No|Number)[:\s]+([\w\d\-\.]+)", text_fallback, re.IGNORECASE)
    if order_alt_match:
        print(f"Fallback 1 Match: {order_alt_match.group(1)}")
    else:
        print("Fallback 1 Failed")

if __name__ == "__main__":
    test_logic()
