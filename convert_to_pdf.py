"""
Simple Markdown to PDF Converter
Converts Delivery_System_Architecture_Report.md to PDF format
"""

import os

def convert_markdown_to_pdf():
    """Convert markdown file to PDF using a simple approach."""
    
    md_file = "Delivery_System_Architecture_Report.md"
    pdf_file = "Delivery_System_Architecture_Report.pdf"
    
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try using reportlab to create PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkgrey
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            leading=14
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Courier',
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.lightgrey
        )
        
        story = []
        
        # Parse markdown and add to story
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('# '):
                story.append(Paragraph(line[2:], title_style))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], heading_style))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], subheading_style))
            elif line.startswith('**') and line.endswith('**'):
                parts = line.split('**')
                if len(parts) >= 3:
                    story.append(Paragraph(parts[1], body_style))
            elif line.startswith('|'):
                # Skip table processing for simplicity
                pass
            elif line.strip() and not line.startswith('---'):
                # Clean markdown symbols
                clean_line = line.replace('**', '').replace('*', '').replace('`', '')
                if clean_line.strip():
                    story.append(Paragraph(clean_line, body_style))
            
            i += 1
        
        # Build PDF
        doc.build(story)
        print(f"PDF generated successfully: {pdf_file}")
        
    except ImportError:
        print("reportlab not installed. Installing...")
        os.system("pip install reportlab")
        convert_markdown_to_pdf()
    except Exception as e:
        print(f"Error creating PDF: {e}")
        print("\nAlternative: Use pandoc to convert:")
        print(f"  pandoc {md_file} -o {pdf_file}")

if __name__ == "__main__":
    convert_markdown_to_pdf()
