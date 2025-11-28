# src/qdrant_client.py

from qdrant_client import QdrantClient, models
from src.config import QDRANT_URL, QDRANT_COLLECTION_NAME, VECTOR_SIZE
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

# Define the Qdrant API parameters used by LangChain
QDRANT_KWARGS = {
    "url": QDRANT_URL,
    # "api_key": os.getenv("QDRANT_API_KEY") # Uncomment if using Qdrant Cloud
}

def get_embedding_model():
    """Initializes and returns the OpenAI Embeddings model."""
    return OpenAIEmbeddings(model="text-embedding-3-small") 

def get_standalone_qdrant_client():
    """Initializes and returns the raw Qdrant client connected to the server."""
    # Use the QDRANT_KWARGS (containing the URL) to connect to the Docker server
    return QdrantClient(**QDRANT_KWARGS)

def get_vector_store():
    """Returns the LangChain Qdrant VectorStore wrapper."""
    # This function is used by retrieval and ingestion services.
    # It must pass the instantiated client object directly to the LangChain wrapper.
    return Qdrant(
        client=get_standalone_qdrant_client(), # Pass the server-connected client
        embeddings=get_embedding_model(),
        collection_name=QDRANT_COLLECTION_NAME,
    )
    
def initialize_qdrant_collection():
    """Ensures the collection exists. Called once during Streamlit setup."""
    client = get_standalone_qdrant_client()
    
    # Define vector parameters
    vectors_config = models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
    
    # Check if collection exists manually and create if necessary
    collections = client.get_collections().collections
    if QDRANT_COLLECTION_NAME not in [c.name for c in collections]:
        print(f"Creating collection '{QDRANT_COLLECTION_NAME}'...")
        
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=vectors_config
        )
        print("Collection created successfully.")
    else:
        print(f"Collection '{QDRANT_COLLECTION_NAME}' already exists. Setup complete.")