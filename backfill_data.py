import os
import glob
import sqlite3
import pdfplumber
import re
import datetime
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Configuration
INPUT_FOLDER = r"\\BRD-DESKTOP-ELV\storage"
DB_PATH = r"C:\Users\Assault\OneDrive\Documents\Delivery Route\delivery.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def extract_order_number(pdf_path):
    """Extract order number using improved regex."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
                
            # Pattern 1: Table column
            order_header_match = re.search(r"Account\s+Date\s+Order\s+No", text, re.IGNORECASE)
            if order_header_match:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if "Account" in line and "Date" in line and "Order" in line:
                        if i + 1 < len(lines):
                            data_line = lines[i+1]
                            data_match = re.search(r"[\w\d]+\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d+)", data_line)
                            if data_match:
                                return data_match.group(2).strip()
            
            # Pattern 2: Explicit Label
            order_alt_match = re.search(r"Order\s*(?:No|Number)[:\s]+(\d+)", text, re.IGNORECASE)
            if order_alt_match:
                return order_alt_match.group(1).strip()

            # Pattern 3: Sales Order
            sales_order_match = re.search(r"Sales\s*Order[:\s]+(\d+)", text, re.IGNORECASE)
            if sales_order_match:
                return sales_order_match.group(1).strip()
            
            # DEBUG: If we get here, no match found. Print text snippet.
            logger.info(f"NO MATCH FOUND in {os.path.basename(pdf_path)}")
            logger.info("--- TEXT SNIPPET START ---")
            logger.info(text[:3000]) # First 3000 chars
            logger.info("--- TEXT SNIPPET END ---")
                
    except Exception as e:
        logger.error(f"Error reading {os.path.basename(pdf_path)}: {e}")
    return None

def backfill_orders():
    logger.info("--- Inspecting Specific Files ---")
    
    # Files to inspect: Known Good vs Known Bad
    target_files = ["BINV8492", "BINV8375"]
    
    # Find these files
    found_files = []
    
    # Search INPUT and PROCESSED folders
    folders_to_check = [
        INPUT_FOLDER,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Invoices_Processed"),
        os.path.join(r"c:\Users\Assault\OneDrive\Documents\Delivery Route", "Invoices_Processed")
    ]
    
    for folder in folders_to_check:
        if not os.path.exists(folder): continue
        for pdf_file in glob.glob(os.path.join(folder, "*.pdf")):
            for target in target_files:
                if target in pdf_file:
                    found_files.append(pdf_file)
    
    # Remove duplicates
    found_files = list(set(found_files))
    
    for pdf_path in found_files:
        logger.info(f"\nProcessing: {os.path.basename(pdf_path)}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                
                # Dump lines around "Account Date"
                logger.info("--- TABLE SNIPPET ---")
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if "Account" in line and "Date" in line:
                        logger.info(f"HEADER: {line}")
                        if i+1 < len(lines):
                            logger.info(f"DATA 1: {lines[i+1]}")
                        if i+2 < len(lines):
                            logger.info(f"DATA 2: {lines[i+2]}")
                
                # Dump header keywords
                logger.info("--- KEYWORDS SNIPPET ---")
                match = re.search(r"Order", text, re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    logger.info(f"...{text[start:end]}...")
                    
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    backfill_orders()
    # backfill_reports() # Skip reports for now
