# check_db.py
from src.qdrant_client import get_standalone_qdrant_client
from src.config import QDRANT_COLLECTION_NAME

def check_database():
    client = get_standalone_qdrant_client()
    
    # 1. Check Collection Info
    try:
        info = client.get_collection(QDRANT_COLLECTION_NAME)
        print(f"--- COLLECTION STATUS ---")
        print(f"Status: {info.status}")
        print(f"Total Vectors: {info.points_count}")
        
        if info.points_count == 0:
            print("⚠️ WARNING: Database is EMPTY. Please run the 'Index Document' step in Streamlit.")
            return

        # 2. Scroll through points to check Metadata
        print(f"\n--- CHECKING LATEST ENTRY ---")
        points = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=1,
            with_payload=True
        )[0]
        
        if points:
            print("Found Payload (Metadata):", points[0].payload)
            if "tenant_id" in points[0].payload:
                print(f"✅ SUCCESS: 'tenant_id' found: {points[0].payload['tenant_id']}")
            else:
                print("❌ ERROR: 'tenant_id' is MISSING from metadata!")
        else:
            print("Database has count > 0 but returned no points. Strange.")
            
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_database()