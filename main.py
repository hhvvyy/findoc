# main.py
import extractor
import chunker
from vector_store import add_documents_to_db

def process_and_store_pdf(pdf_path: str):
    """
    The main ingestion pipeline. Extracts, chunks, and stores a PDF.
    """
    #print(f"--- Starting Ingestion Pipeline for: {pdf_path} ---")
    
    # 1. Extract text from the PDF path provided
    page_text = extractor.extract_text(pdf_path)
    
    # 2. Break it into chunks
    chunks = chunker.chunk_text(page_text)
    
    # 3. Pass the chunks directly to our database function to be saved    
    add_documents_to_db(chunks)
    
   # print(f"--- Successfully processed and stored {len(chunks)} chunks! ---")