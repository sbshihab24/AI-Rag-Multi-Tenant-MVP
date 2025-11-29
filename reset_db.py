from src.qdrant_client import get_standalone_qdrant_client
from src.config import QDRANT_COLLECTION_NAME
from qdrant_client import models
from src.config import VECTOR_SIZE

def reset_collection():
    print(f"CONNECTING TO QDRANT...")
    client = get_standalone_qdrant_client()
    
    print(f"DELETING COLLECTION: {QDRANT_COLLECTION_NAME}")
    client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)
    
    print(f"RE-CREATING COLLECTION: {QDRANT_COLLECTION_NAME}")
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE, 
            distance=models.Distance.COSINE
        )
    )
    print("SUCCESS: Database has been wiped and reset.")

if __name__ == "__main__":
    reset_collection()