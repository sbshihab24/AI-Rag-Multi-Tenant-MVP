# src/rag/retrieval.py

from langchain_core.documents import Document
from qdrant_client import models
from src.qdrant_client import get_standalone_qdrant_client, get_embedding_model
from src.config import QDRANT_COLLECTION_NAME

# CHANGE: Increase default k from 8 to 15
def get_tenant_docs(query: str, tenant_id: str, k: int = 15): 
    """
    Manually retrieves documents. Increased k to 15 to handle 'noise' from large documents.
    """
    client = get_standalone_qdrant_client()
    embedding_model = get_embedding_model()
    
    # 1. Generate Query Embedding
    query_vector = embedding_model.embed_query(query)
    
    # ... (Filter definition remains the same) ...
    
    # 3. Execute Search
    results_obj = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        query_filter=tenant_filter,
        limit=k, # This now uses the higher limit (15)
        with_payload=True
    )
    
    # 4. Handle Response Format (Robustness)
    if hasattr(results_obj, 'points'):
        points = results_obj.points
    else:
        points = results_obj

    # 5. Convert to LangChain Documents
    docs = []
    for point in points:
        payload = point.payload or {}
        
        # CRITICAL FIX: Unwrap the nested 'metadata' dictionary
        # Qdrant stores it as {'page_content': '...', 'metadata': {...}}
        # We need that inner dict for our citations.
        real_metadata = payload.get('metadata', payload)
        
        doc = Document(
            page_content=payload.get('page_content', ''),
            metadata=real_metadata
        )
        docs.append(doc)
        
    return docs

def format_retrieved_context(docs: list[Document]):
    """Formats retrieved documents into context text and citations."""
    context_list = []
    citation_list = []

    for doc in docs:
        source = doc.metadata.get('source', 'Unknown Document')
        # Handle page number being an int or string
        page = doc.metadata.get('page', 'N/A')
        
        citation = f"{source} (Page {page})"
        citation_list.append(citation)
        
        # Concatenate context with citation metadata
        context_list.append(f"Source: {citation}\nContent: {doc.page_content}")

    return "\n\n---\n\n".join(context_list), list(set(citation_list))