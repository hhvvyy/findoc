# extractor.py
import pdfplumber

def extract_text(pdf_path):
    page_text = ""
    
    # Open the PDF file safely
    with pdfplumber.open(pdf_path) as pdf:
        
        # Loop through every single page sequentially
        for index, page in enumerate(pdf.pages):
            
            # Extract the raw text from the current page
            extracted_text = page.extract_text()
            
            # SAFETY CHECK: Only add text if it actually found some
            if extracted_text:
                page_text += extracted_text + "\n"
                
    return page_text