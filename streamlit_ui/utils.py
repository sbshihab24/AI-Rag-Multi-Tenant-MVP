# streamlit_ui/utils.py

import streamlit as st
from src.qdrant_client import initialize_qdrant_collection
import json

# --- Function only contains code that must run once and be cached ---
@st.cache_resource(show_spinner="Initializing Database and Vector Store...")
def initialize_backend_setup():
    """Initializes and sets up the non-UI backend components (DB and Qdrant)."""
    # Import database setup here to avoid circular dependency with models/session state
    from src.database import init_db 
    
    init_db()
    initialize_qdrant_collection() 

def show_login_form():
    """Displays the login form for tenant selection."""
    from src.config import TENANT_IDS, ADMIN_ID
    
    st.title("Multi-Tenant RAG Assistant MVP")
    
    tenant_list = TENANT_IDS + [ADMIN_ID]
    selected_tenant = st.selectbox("Select User Role:", tenant_list)
    
    if st.button("Access Application"):
        # Reset chat history when changing users
        st.session_state.messages = [] 
        st.session_state.tenant_id = selected_tenant
        st.success(f"Logged in as {selected_tenant}. Please refresh the page.")
        # Streamlit will automatically refresh upon session state change
        
def display_chat_history():
    """Displays the conversation history from session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["citations"]:
                # Ensure citations are strings before joining
                st.caption("Sources: " + ", ".join(map(str, json.loads(message["citations"]))))

def get_admin_logs():
    """Fetches conversation logs for admin panel."""
    from src.database import get_all_logs # Import locally to avoid circular dependency
    return get_all_logs()