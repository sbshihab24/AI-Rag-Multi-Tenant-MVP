# src/ingestion/storage.py

from datetime import datetime
from src.database import SessionLocal, Document
from src.ingestion.doc_loader import load_and_split_document, save_uploaded_file
from src.qdrant_client import upsert_documents   # ← NEW FIXED IMPORT


def ingest_document(uploaded_file, tenant_id: str):
    """
    Ingests a single uploaded document:
      1) Saves the file into the tenant's folder
      2) Extracts text + splits into chunks
      3) Embeds chunks and stores vectors per tenant
      4) Logs ingestion into SQLite
    """
    file_name = uploaded_file.name

    # -----------------------------------------------------------
    # 1. Save uploaded file
    # -----------------------------------------------------------
    try:
        file_path = save_uploaded_file(uploaded_file, tenant_id)
    except Exception as e:
        return f"FAILED: Could not save uploaded file: {e}"

    # -----------------------------------------------------------
    # 2. Extract text + split into chunks
    # -----------------------------------------------------------
    error, chunks = load_and_split_document(file_path, file_name, tenant_id)

    if error:
        return f"FAILED: {error}"

    if not chunks:
        return "Warning: No extractable text found in the document."

    # -----------------------------------------------------------
    # 3. Store embeddings in Qdrant (per-tenant collection)
    # -----------------------------------------------------------
    try:
        vector_count = upsert_documents(tenant_id, chunks)
    except Exception as e:
        return f"FAILED: Qdrant ingestion error: {e}"

    # -----------------------------------------------------------
    # 4. Log ingestion in the database
    # -----------------------------------------------------------
    db = SessionLocal()
    try:
        new_doc = Document(
            tenant_id=tenant_id,
            file_name=file_name,
            upload_date=datetime.utcnow(),
            vector_count=vector_count
        )
        db.add(new_doc)
        db.commit()
    except Exception as e:
        db.rollback()
        return f"FAILED: DB logging error: {e}"
    finally:
        db.close()

    return f"Success ({vector_count} chunks embedded)"
