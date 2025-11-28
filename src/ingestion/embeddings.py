# src/ingestion/embeddings.py

from openai import OpenAI
from src.config import OPENAI_API_KEY, EMBEDDING_MODEL

# Initialize OpenAI client globally
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a list of texts using the OpenAI API."""
    try:
        response = openai_client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL
        )
        # Extract the vector list from the response
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []