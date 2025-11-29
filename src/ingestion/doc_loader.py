# src/ingestion/doc_loader.py

import os
import re
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader, 
    TextLoader, 
    CSVLoader, 
    UnstructuredExcelLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

def get_loader_for_file(file_path: str):
    """Factory function to choose the right loader based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext == ".docx":
        return Docx2txtLoader(file_path)
    elif ext in [".txt", ".md"]:
        return TextLoader(file_path, encoding="utf-8")
    elif ext == ".csv":
        return CSVLoader(file_path, encoding="utf-8")
    elif ext in [".xlsx", ".xls"]:
        # Note: Might require 'pip install openpyxl'
        return UnstructuredExcelLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def load_and_split_document(file_path: str, file_name: str, tenant_id: str):
    """Universal loader that handles multiple formats, splits, and tags metadata."""
    
    # 1. Select the correct loader
    try:
        loader = get_loader_for_file(file_path)
        documents = loader.load()
    except Exception as e:
        return f"Error loading {file_name}: {str(e)}", []

    # 2. Split Text (Universal chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""] # Try to keep paragraphs together
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Add Multi-Tenant Metadata
    for chunk in chunks:
        chunk.metadata["tenant_id"] = tenant_id
        chunk.metadata["source"] = file_name
    
    return None, chunks # Error is None if successful

def save_uploaded_file(uploaded_file, tenant_id: str):
    """Saves any uploaded file to the local cache."""
    base_dir = Path("data") / "source_docs" / tenant_id
    base_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename to avoid invalid characters on Windows and directory traversal
    original_name = os.path.basename(uploaded_file.name)
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
    file_path = base_dir / safe_name

    # Try writing directly, fall back to unique filename on PermissionError
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(file_path)
    except PermissionError:
        logger.exception("Permission denied when writing file %s", file_path)
        # Try alternate filename with timestamp suffix
        unique_name = f"{file_path.stem}_{int(time.time())}{file_path.suffix}"
        unique_path = base_dir / unique_name
        try:
            with open(unique_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info("Saved uploaded file to alternate path %s", unique_path)
            return str(unique_path)
        except Exception:
            logger.exception("Failed to write alternate file %s", unique_path)
            # Re-raise to let caller handle the error (ingest_document will catch it)
            raise
    except Exception:
        logger.exception("Unexpected error when saving uploaded file %s", file_path)
        raise