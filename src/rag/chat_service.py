# src/rag/chat_service.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Import the new manual retrieval function
from src.rag.retrieval import get_tenant_docs, format_retrieved_context
from src.rag.prompt_templates import SYSTEM_PROMPT
from src.config import OPENAI_API_KEY, LLM_MODEL
from src.database import log_conversation
import json

def get_rag_response(query: str, tenant_id: str):
    """
    Main service function for RAG: manually retrieves context, calls LLM, and logs interaction.
    """
    
    answer = ""
    citations_list = []

    try:
        # 1. Initialize LLM
        llm = ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0)
        
        # 2. Retrieve Documents (Using Manual Qdrant Call)
        # This bypasses the 'retriever.invoke' error
        retrieved_docs = get_tenant_docs(query, tenant_id)
        
        # 3. Format Context and Citations
        context, citations_list = format_retrieved_context(retrieved_docs)
        
        # Handle case where no documents are found
        if not context:
            answer = "I cannot answer this question based on the tenant's documents provided."
            citations_json = json.dumps([])
            log_conversation(tenant_id, query, answer, citations_json)
            return answer, []

        # 4. Construct the Messages for the LLM
        formatted_system_prompt = SYSTEM_PROMPT.format(context=context, question=query)
        
        messages = [
            SystemMessage(content=formatted_system_prompt),
            HumanMessage(content=query)
        ]

        # 5. Generate Response
        response_message = llm.invoke(messages)
        answer = response_message.content

    except Exception as e:
        answer = f"An error occurred during RAG processing: {str(e)}"
        citations_list = ["Error"]
        print(f"RAG Error: {e}") 
        
    # 6. Log Conversation to SQLite
    citations_json = json.dumps(citations_list)
    log_conversation(tenant_id, query, answer, citations_json)

    return answer, citations_list