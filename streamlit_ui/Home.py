# streamlit_ui/Home.py

import sys
import os
from pathlib import Path

# --- FIX 1: Add the project root to the system path to enable imports from 'src' and 'streamlit_ui' ---
current_file_dir = Path(__file__).resolve().parent
project_root = current_file_dir.parent
sys.path.insert(0, str(project_root))
# -----------------------------------------------------------------------------------------------------

import streamlit as st
from streamlit_ui.utils import show_login_form, initialize_backend_setup
import logging
import sys

# Configure logging to stdout so Streamlit terminal shows backend logs
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# --- FIX 2: Immediate Session State Initialization ---
# This ensures 'tenant_id' exists BEFORE any conditional checks below
if 'tenant_id' not in st.session_state:
    st.session_state.tenant_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- FIX 3: Run complex setup only once via the utility function ---
# This executes DB/Qdrant initialization using Streamlit's cache_resource decorator.
initialize_backend_setup()


st.set_page_config(
    page_title="RAG Multi-Tenant MVP",
    layout="wide"
)

# --- Routing Logic ---
if st.session_state.tenant_id is None:
    # Show the login/selection screen if no tenant is set
    show_login_form()
elif st.session_state.tenant_id == 'admin':
    st.header("Admin Panel Access")
    st.sidebar.success("Navigate to '3 Admin Panel' to view logs.")
else:
    st.header(f"Welcome, {st.session_state.tenant_id}")
    st.sidebar.success(f"Navigate to the Chat page for {st.session_state.tenant_id}")