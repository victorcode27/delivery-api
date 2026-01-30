from PIL import Image, ImageDraw, ImageFont
import os

def create_pdf(filename, content):
    input_folder = r"C:\Users\Assault\OneDrive\Documents\Delivery Route\Invoices_Input"
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        
    width = 800
    height = 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    y = 50
    for line in content:
        draw.text((50, y), line, fill="black", font=font)
        y += 30
        
    pdf_path = os.path.join(input_folder, filename)
    image.save(pdf_path, "PDF", resolution=100.0)
    print(f"Created PDF at: {pdf_path}")

def main():
    # 1. Standard Invoice for Full Cancellation
    create_pdf("BINV_TEST_01.pdf", [
        "INVOICE",
        "",
        "Customer: Test Client One",
        "Invoice No: BINV_TEST_01",
        "Date: 2026-01-25",
        "",
        "Total Value: 100.00"
    ])

    # 2. Standard Invoice for Partial Credit
    create_pdf("BINV_TEST_02.pdf", [
        "INVOICE",
        "",
        "Customer: Test Client Two",
        "Invoice No: BINV_TEST_02",
        "Date: 2026-01-25",
        "",
        "Total Value: 200.00"
    ])

    # 3. Full Credit Note for BINV_TEST_01
    create_pdf("BCRN_TEST_01.pdf", [
        "CREDIT NOTE",
        "",
        "Customer: Test Client One",
        "Invoice No: BCRN_TEST_01",
        "Reference No BINV_TEST_01",
        "",
        "Invoice Total: 100.00"
    ])

    # 4. Partial Credit Note for BINV_TEST_02
    create_pdf("BCRN_TEST_02.pdf", [
        "CREDIT NOTE",
        "",
        "Customer: Test Client Two",
        "Invoice No: BCRN_TEST_02",
        "Reference No BINV_TEST_02",
        "",
        "Invoice Total: 50.00"
    ])

if __name__ == "__main__":
    main()
