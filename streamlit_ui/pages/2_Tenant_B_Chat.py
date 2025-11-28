import streamlit as st
import json

# --- FIX 1: Import the correct new function name ---
from streamlit_ui.utils import initialize_backend_setup, display_chat_history
from src.rag.chat_service import get_rag_response
from src.ingestion.storage import ingest_document

TENANT_ID = "tenantB"

# --- FIX 2: Call the correct backend setup function ---
initialize_backend_setup()

# --- Security Check ---
if 'tenant_id' not in st.session_state:
    st.session_state.tenant_id = None

if st.session_state.tenant_id != TENANT_ID:
    st.error(f"Access Denied. Please log in as {TENANT_ID} on the Home page.")
    st.stop()

st.title(f"🏢 {TENANT_ID} - Knowledge Assistant Chat")
st.markdown("---")

# --- 1. Document Upload and Ingestion ---
with st.expander("Upload Documents"):
    uploaded_file = st.file_uploader(f"Upload PDF for {TENANT_ID}", type="pdf", key=f"uploader_{TENANT_ID}")
    if uploaded_file and st.button(f"Index Document for {TENANT_ID}", key=f"index_btn_{TENANT_ID}"):
        with st.spinner("Processing and indexing document..."):
            try:
                message = ingest_document(uploaded_file, TENANT_ID)
                st.success(f"Indexing complete! {message}")
            except Exception as e:
                st.error(f"Error during ingestion: {e}")

# --- 2. Chat Interface ---
display_chat_history()

if prompt := st.chat_input("Ask a question based on your documents..."):
    user_message = {"role": "user", "content": prompt, "citations": "[]"}
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Searching knowledge base and generating response..."):
        answer, citations = get_rag_response(prompt, TENANT_ID)

    citations_json = json.dumps(citations)
    assistant_message = {"role": "assistant", "content": answer, "citations": citations_json}
    st.session_state.messages.append(assistant_message)
    
    with st.chat_message("assistant"):
        st.markdown(answer)
        if citations:
            st.caption("Sources: " + ", ".join(citations))