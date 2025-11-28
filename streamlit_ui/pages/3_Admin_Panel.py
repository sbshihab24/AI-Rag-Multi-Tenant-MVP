# streamlit_ui/pages/3_Admin_Panel.py

import streamlit as st
import pandas as pd
from streamlit_ui.utils import initialize_app_state, get_admin_logs
from src.config import ADMIN_ID

initialize_app_state()

if st.session_state.tenant_id != ADMIN_ID:
    st.error("Access Denied. Only Admin users can view this page.")
    st.stop()

st.title("🛡️ Admin Panel - Q&A Logs")
st.markdown("---")

# --- 1. View Logs ---
logs = get_admin_logs()

if logs:
    st.subheader("All Conversation Logs")
    
    # Convert logs to DataFrame for easy display
    df = pd.DataFrame(logs)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Display the logs
    st.dataframe(df, use_container_width=True)
    
    # NOTE: The "Correct an answer & save it as validated" feature would be implemented here
    # by adding a form/button that updates the 'is_validated' and 'answer' fields 
    # in the ConversationLog table via a new function in src/database.py.
else:
    st.info("No conversation logs found in the database.")

# --- 2. Tenant Management (Placeholder) ---
st.markdown("---")
st.subheader("Tenant Management")
st.warning("Tenant deletion logic (removing files, DB records, and Qdrant vectors) is complex and requires careful implementation.")
st.button("Delete Tenant (Logic Placeholder)", disabled=True)