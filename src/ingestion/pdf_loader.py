# src/ingestion/pdf_loader.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
import os

def load_and_split_pdf(file_path: str, file_name: str, tenant_id: str):
    """Loads a PDF, splits it into chunks, and adds required metadata."""
    
    # 1. Load PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # 2. Split into Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Add Custom Metadata (CRITICAL FIX)
    # We must iterate through every chunk and explicitely tag it with the tenant_id
    for chunk in chunks:
        chunk.metadata["tenant_id"] = tenant_id 
        chunk.metadata["source"] = file_name
        # 'page' metadata is automatically added by PyPDFLoader

    return chunks

def save_uploaded_file(uploaded_file, tenant_id: str):
    """Saves the uploaded file to the local data folder."""
    base_dir = f"./data/pdf_source/{tenant_id}"
    os.makedirs(base_dir, exist_ok=True)
    file_path = os.path.join(base_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return file_path