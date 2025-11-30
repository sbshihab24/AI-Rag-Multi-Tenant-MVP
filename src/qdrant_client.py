# # src/qdrant_client.py

# from qdrant_client import QdrantClient, models
# from src.config import QDRANT_URL, QDRANT_COLLECTION_NAME, VECTOR_SIZE
# from langchain_community.vectorstores import Qdrant
# from langchain_openai import OpenAIEmbeddings
# import logging

# logger = logging.getLogger(__name__)

# # Define the Qdrant API parameters
# QDRANT_KWARGS = {
#     "url": QDRANT_URL,
#     # "api_key": os.getenv("QDRANT_API_KEY") # Uncomment if using Cloud
# }

# def get_embedding_model():
#     """Initializes and returns the OpenAI Embeddings model."""
#     return OpenAIEmbeddings(model="text-embedding-3-small") 

# def get_standalone_qdrant_client():
#     """Initializes and returns the raw Qdrant client connected to the server."""
#     return QdrantClient(**QDRANT_KWARGS)

# def get_vector_store():
#     """Returns the LangChain Qdrant VectorStore wrapper."""
#     # This is used for INGESTION (Adding documents)
#     return Qdrant(
#         client=get_standalone_qdrant_client(),
#         embeddings=get_embedding_model(),
#         collection_name=QDRANT_COLLECTION_NAME,
#     )
    
# def initialize_qdrant_collection():
#     """Ensures the collection exists. Called once during Streamlit setup."""
#     client = get_standalone_qdrant_client()
    
#     # Define vector parameters
#     vectors_config = models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
    
#     # Check if collection exists manually and create if necessary
#     collections = client.get_collections().collections
#     if QDRANT_COLLECTION_NAME not in [c.name for c in collections]:
#         logger.info(f"Creating collection '{QDRANT_COLLECTION_NAME}'...")
#         client.recreate_collection(
#             collection_name=QDRANT_COLLECTION_NAME,
#             vectors_config=vectors_config
#         )
#         logger.info("Collection created successfully.")





# src/qdrant_client.py

from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# ✔ Always use in-memory Qdrant for Streamlit (no Docker needed)
# ------------------------------------------------------------
_qdrant_client = QdrantClient(path=":memory:")

def get_qdrant_client():
    """Return the global in-memory Qdrant client."""
    return _qdrant_client


# ------------------------------------------------------------
# ✔ Embedding model using OpenAI (no LangChain)
# ------------------------------------------------------------
from openai import OpenAI
import os

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_texts(texts):
    """Returns embeddings for a list of texts using OpenAI API."""
    resp = openai.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [d.embedding for d in resp.data]


# ------------------------------------------------------------
# ✔ Create collection per tenant
# ------------------------------------------------------------
def ensure_collection(tenant_id, vector_size=1536):
    """Create a separate vector collection for each tenant."""
    client = get_qdrant_client()
    collection_name = f"{tenant_id}_docs"

    existing = client.get_collections().collections
    if collection_name in [c.name for c in existing]:
        return collection_name

    logger.info(f"Creating Qdrant collection for {tenant_id}")

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE
        )
    )
    return collection_name


# ------------------------------------------------------------
# ✔ Add documents to tenant-specific collection
# ------------------------------------------------------------
def upsert_documents(tenant_id, chunks):
    """
    chunks = [
      {
          "id": "...",
          "text": "...",
          "source_file": "...",
          "page": 1
      }
    ]
    """

    client = get_qdrant_client()
    collection = ensure_collection(tenant_id)

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(
            models.PointStruct(
                id=chunk["id"],
                vector=vector,
                payload=chunk
            )
        )

    client.upsert(
        collection_name=collection,
        points=points
    )

    return len(points)


# ------------------------------------------------------------
# ✔ Query tenant-specific collection only
# ------------------------------------------------------------
def query_documents(tenant_id, query_text, top_k=5):
    client = get_qdrant_client()
    collection = ensure_collection(tenant_id)

    query_vector = embed_texts([query_text])[0]

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )

    return results
