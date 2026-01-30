from PIL import Image, ImageDraw, ImageFont
import os

def create_test_pdf():
    # Create the input folder if it doesn't exist
    input_folder = r"C:\Users\Assault\OneDrive\Documents\Delivery Route\Invoices_Input"
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        
    width = 800
    height = 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # Try to load a default font, otherwise use default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    text_content = [
        "INVOICE",
        "",
        "Customer House No: 1234 TEST CUSTOMER LTD",
        "Telephone: 555-0199",
        "",
        "Date: 2026-01-26",
        "",
        "Account   Date       Order No",
        "TEST001   26/01/2026 SO-9988-XY",  # Alphanumeric test case
        "",
        "Description           Amount",
        "----------------------------",
        "Widget A              $50.00",
        "",
        "Invoice Total:        $50.00",
        "Invoice No:           BINV_TEST_001"
    ]
    
    y = 50
    for line in text_content:
        draw.text((50, y), line, fill="black", font=font)
        y += 30
        
    pdf_path = os.path.join(input_folder, "test_invoice_001.pdf")
    image.save(pdf_path, "PDF", resolution=100.0)
    print(f"Created test PDF at: {pdf_path}")

if __name__ == "__main__":
    create_test_pdf()
