from langchain_core.documents import Document
from qdrant_client import models
from src.qdrant_client import get_standalone_qdrant_client, get_embedding_model
from src.config import QDRANT_COLLECTION_NAME

def get_tenant_docs(query: str, tenant_id: str, k: int = 15):
    """
    Manually retrieves documents using Qdrant's query_points method.
    Strictly enforces tenant isolation via metadata filtering.
    """
    if not tenant_id:
        print("Error: No tenant_id provided for retrieval.")
        return []

    client = get_standalone_qdrant_client()
    embedding_model = get_embedding_model()
    
    # 1. Generate Query Embedding
    query_vector = embedding_model.embed_query(query)
    
    # 2. Define Tenant Filter (STRICT)
    # We filter by 'metadata.tenant_id' because LangChain nests the metadata
    tenant_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.tenant_id", 
                match=models.MatchValue(value=tenant_id)
            )
        ]
    )
    
    # 3. Execute Search
    results_obj = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        query_filter=tenant_filter, # STRICT FILTER APPLIED HERE
        limit=k,
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
        
        # Unwrap nested metadata if present
        real_metadata = payload.get('metadata', payload)
        
        # DOUBLE CHECK: Ensure the retrieved document actually belongs to the tenant
        # This acts as a second layer of safety.
        retrieved_tenant = real_metadata.get('tenant_id')
        if retrieved_tenant != tenant_id:
            print(f"WARNING: Retrieved document for {retrieved_tenant} but requested {tenant_id}. Skipping.")
            continue

        doc = Document(
            page_content=payload.get('page_content', ''),
            metadata=real_metadata
        )
        docs.append(doc)
        
    return docs

def format_retrieved_context(docs: list[Document]):
    """Formats retrieved documents into context text and citations."""
    if not docs:
        return "", []

    context_list = []
    citation_list = []

    for doc in docs:
        source = doc.metadata.get('source', 'Unknown Document')
        # Handle page number being int/str or missing
        page = doc.metadata.get('page', 'N/A')
        
        citation = f"{source} (Page {page})"
        citation_list.append(citation)
        
        # Concatenate context with citation metadata
        context_list.append(f"Source: {citation}\nContent: {doc.page_content}")

    return "\n\n---\n\n".join(context_list), list(set(citation_list))