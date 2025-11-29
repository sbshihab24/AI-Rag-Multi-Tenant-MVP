# src/ingestion/storage.py

from src.qdrant_client import get_vector_store
from src.ingestion.doc_loader import load_and_split_document, save_uploaded_file
from src.database import SessionLocal, Document
from datetime import datetime

def ingest_document(uploaded_file, tenant_id: str):
    """Ingests a single file of ANY supported type."""
    file_name = uploaded_file.name
    
    # 1. Save File
    try:
        file_path = save_uploaded_file(uploaded_file, tenant_id)
    except Exception as e:
        return f"FAILED: Could not save uploaded file: {e}"
    
    # 2. Load & Split (Using the new Universal Loader)
    error, chunks = load_and_split_document(file_path, file_name, tenant_id)
    
    if error:
        return f"FAILED: {error}"
    
    if not chunks:
        return "Warning: No text found in document."

    # 3. Store in Qdrant (Merging into existing KB automatically)
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    
    # 4. Log to DB
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
        
    return f"Success ({len(chunks)} chunks)"