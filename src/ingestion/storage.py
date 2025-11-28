# src/ingestion/storage.py

from src.qdrant_client import get_vector_store
from src.ingestion.pdf_loader import load_and_split_pdf, save_uploaded_file
from src.database import SessionLocal, Document
from datetime import datetime

def ingest_document(uploaded_file, tenant_id: str):
    """Main function to handle full document ingestion pipeline."""
    file_name = uploaded_file.name
    
    # 1. Save File Locally
    file_path = save_uploaded_file(uploaded_file, tenant_id)
    
    # 2. Load and Split PDF
    chunks = load_and_split_pdf(file_path, file_name, tenant_id)
    
    # 3. Store in Qdrant
    # We use the existing vector_store instance to avoid connection errors
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    
    # 4. Log to SQLite
    db = SessionLocal()
    try:
        new_doc = Document(
            tenant_id=tenant_id,
            file_name=file_name,
            upload_date=datetime.utcnow(),
            vector_count=len(chunks)
        )
        db.add(new_doc)
        db.commit()
    finally:
        db.close()
        
    return f"Indexed {len(chunks)} chunks into Qdrant."