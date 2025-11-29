import streamlit as st
import time
import json
from streamlit_ui.utils import initialize_backend_setup
from src.rag.chat_service import get_rag_response
from src.ingestion.storage import ingest_document

TENANT_ID = "tenantA"
initialize_backend_setup()

# ============================
#  PERFECT CHATGPT-STYLE CSS
# ============================
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

# ============================
#  TENANT ACCESS
# ============================
if 'tenant_id' not in st.session_state:
    st.session_state.tenant_id = None

if st.session_state.tenant_id != TENANT_ID:
    st.error(f"Access Denied. Log in as {TENANT_ID}.")
    st.stop()

st.title(f"🤖 tenantA Knowledge Chat")


# ============================
#  DOCUMENT UPLOAD
# ============================
with st.expander("📁 Add Documents"):
    uploaded_files = st.file_uploader(
        "Upload files", type=["pdf","docx","txt","csv","xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process Documents"):
        progress = st.progress(0)
        for i, file in enumerate(uploaded_files):
            ingest_document(file, TENANT_ID)
            progress.progress((i+1)/len(uploaded_files))
        st.success("All documents processed!")


# ============================
#  CHAT DISPLAY (History)
# ============================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"

    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

        if msg.get("citations") and msg["citations"] != "[]":
            with st.expander("📚 Sources"):
                for src in json.loads(msg["citations"]):
                    st.caption(src)


# ============================
#  USER INPUT
# ============================
if prompt := st.chat_input("Ask a question..."):

    # user bubble
    st.session_state.messages.append({"role": "user", "content": prompt, "citations": []})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # assistant bubble
    with st.chat_message("assistant", avatar="🤖"):
        resp_box = st.empty()
        with st.spinner("Thinking..."):
            answer, citations = get_rag_response(prompt, TENANT_ID)

        resp_box.markdown(answer)

        if citations:
            with st.expander("📚 Sources"):
                for src in citations:
                    st.caption(src)

    # save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "citations": json.dumps(citations)
    })
