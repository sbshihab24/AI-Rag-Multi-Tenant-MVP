import streamlit as st
import time
import json
from streamlit_ui.utils import initialize_backend_setup
from src.rag.chat_service import get_rag_response
from src.ingestion.storage import ingest_document

# --- TENANT CONFIGURATION ---
TENANT_ID = "tenantB"  # <--- Unique to this page
# ----------------------------

initialize_backend_setup()

# --- 1. FINANCE AI ASSISTANT STYLE CSS ---
# This CSS is identical to Tenant A to ensure UI consistency across the platform
st.markdown("""
<style>

    .stChatMessage {
        background: transparent !important;
    }

    /* ================================
       USER → RIGHT
       ================================ */
    .stChatMessage[class*="user"] {
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: flex-end !important;
        align-items: flex-start !important;
    }

    .stChatMessage[class*="user"] .stChatMessageContent div[data-testid="stMarkdownContainer"] {
        background: #d9e7ff !important;   /* soft blue */
        padding: 16px 20px !important;
        border-radius: 18px 18px 0px 18px !important;
        max-width: 75%;
        margin-left: auto !important;
        margin-right: 8px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }


    /* ================================
       ASSISTANT → LEFT
       ================================ */
    .stChatMessage[class*="assistant"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
    }

    .stChatMessage[class*="assistant"] .stChatMessageContent div[data-testid="stMarkdownContainer"] {
        background: #ffffff !important;
        padding: 16px 20px !important;
        border-radius: 18px 18px 18px 0px !important;
        max-width: 75%;
        margin-right: auto !important;
        margin-left: 8px !important;
        border: 1px solid #ececec;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }


    /* ================================
       AVATAR
       ================================ */
    .stChatMessageAvatar {
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        border: 1px solid #cccccc !important;
        background: white;
        padding: 4px !important;
    }

</style>
""", unsafe_allow_html=True)

# --- Security & Setup ---
# Ensure session state exists before checking it
if 'tenant_id' not in st.session_state:
    st.session_state.tenant_id = None

if st.session_state.tenant_id != TENANT_ID:
    st.error(f"Access Denied. Please log in as {TENANT_ID} on the Home page.")
    st.stop()

# Header Style
st.markdown(f"<h1 style='text-align: center; color: #1a1a1a;'>🤖 {TENANT_ID} Knowledge Chat</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666; margin-bottom: 30px;'>Ask questions about your uploaded documents.</p>", unsafe_allow_html=True)

# --- 2. Multi-File Upload Widget ---
with st.expander("📂 Add Documents to Knowledge Base", expanded=False):
    uploaded_files = st.file_uploader(
        f"Upload PDF, DOCX, TXT, CSV, Excel for {TENANT_ID}", 
        type=["pdf", "docx", "txt", "md", "csv", "xlsx"], 
        accept_multiple_files=True
    )
    if uploaded_files and st.button(f"Process {len(uploaded_files)} Documents"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Ingesting file {i+1}/{len(uploaded_files)}: {file.name}...")
            ingest_document(file, TENANT_ID)
            progress_bar.progress((i + 1) / len(uploaded_files))
        status_text.success("✅ Complete!")

# --- 3. Chat Logic ---

# Display History
for msg in st.session_state.messages:
    icon = "👤" if msg["role"] == "user" else "🤖"
    
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])
        
        # Sources logic
        if msg.get("citations") and msg["citations"] != "[]" and "Error" not in msg["citations"]:
            with st.expander("📚 Sources"):
                sources = json.loads(msg["citations"])
                for source in sources:
                    st.caption(source)

# User Input
if prompt := st.chat_input("Ask a question..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt, "citations": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Assistant Message
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            time.sleep(0.3) 
            answer, citations = get_rag_response(prompt, TENANT_ID)
        
        message_placeholder.markdown(answer)
        
        if citations and "Error" not in citations:
            with st.expander("📚 Sources"):
                for source in citations:
                    st.caption(source)
    
    # 3. Save Assistant Response
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer, 
        "citations": json.dumps(citations)
    })