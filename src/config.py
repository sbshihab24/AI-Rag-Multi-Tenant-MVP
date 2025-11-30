import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "multi_tenant_knowledge")
VECTOR_SIZE = 1536

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TENANT_IDS = ["tenantA", "tenantB", "tenantC"]
ADMIN_ID = "admin"
