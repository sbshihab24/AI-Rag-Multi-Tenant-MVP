# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.models import Base, Tenant, Document, ConversationLog
# from src.config import DATABASE_URL
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# # Initialize Engine and Session
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def init_db():
#     """Create tables and pre-populate initial tenants if they don't exist."""
#     Base.metadata.create_all(bind=engine)
    
#     db = SessionLocal()
#     try:
#         # Pre-populate tenants for the demo
#         if db.query(Tenant).count() == 0:
#             db.add_all([
#                 Tenant(id="tenantA", name="Tenant Alpha Corp"),
#                 Tenant(id="tenantB", name="Tenant Beta Solutions"),
#                 # ADD THIS LINE:
#                 Tenant(id="tenantC", name="Tenant Charlie Inc"), 
#                 Tenant(id="admin", name="Admin Panel User")
#             ])
#             db.commit()
#             logger.info("Initial tenants created.")
#     except Exception as e:
#         logger.exception(f"DB setup error: {e}")
#         db.rollback()
#     finally:
#         db.close()

# # --- Logging Functions ---

# def log_conversation(tenant_id: str, question: str, answer: str, citations: str):
#     """Saves a Q&A interaction to the database."""
#     db = SessionLocal()
#     try:
#         log = ConversationLog(
#             tenant_id=tenant_id,
#             question=question,
#             answer=answer,
#             citations=citations,
#             timestamp=datetime.utcnow()
#         )
#         db.add(log)
#         db.commit()
#     finally:
#         db.close()

# def get_all_logs():
#     """Retrieves all conversation logs for the Admin Panel."""
#     db = SessionLocal()
#     try:
#         # Join with Tenant table to show tenant names
#         # results will be a list of tuples: (ConversationLog, tenant_name)
#         results = db.query(ConversationLog, Tenant.name).join(Tenant).all()
        
#         logs_list = []
#         for log, tenant_name in results:
#             logs_list.append({
#                 "id": log.id, # Corrected: Access 'id' directly on the ConversationLog object 'log'
#                 "tenant_name": tenant_name,
#                 "question": log.question,
#                 "answer": log.answer,
#                 "timestamp": log.timestamp
#             })
#         return logs_list
#     finally:
#         db.close()



# src/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Tenant, Document, ConversationLog
from src.config import DATABASE_URL
from datetime import datetime

# Initialize Engine and Session
# Note: We strictly use the URL from config. The folder creation happens in init_db.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables and pre-populate initial tenants if they don't exist."""
    
    # --- FIX: Ensure the database directory exists before creating the file ---
    if DATABASE_URL.startswith("sqlite:///"):
        # Extract the path (e.g., "./data/mvp_database.db")
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        
        # If a directory path exists and it's not empty, create it
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
            except Exception as e:
                print(f"Warning: Could not create DB directory. Error: {e}")
    # -------------------------------------------------------------------------

    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Pre-populate tenants for the demo
        # We check for tenants to avoid duplicates on restarts
        if db.query(Tenant).count() == 0:
            db.add_all([
                Tenant(id="tenantA", name="Tenant Alpha Corp"),
                Tenant(id="tenantB", name="Tenant Beta Solutions"),
                Tenant(id="tenantC", name="Tenant Charlie Inc"),
                Tenant(id="admin", name="Admin Panel User")
            ])
            db.commit()
            print("Initial tenants created.")
    except Exception as e:
        print(f"DB setup error: {e}")
        db.rollback()
    finally:
        db.close()

# --- Logging Functions ---

def log_conversation(tenant_id: str, question: str, answer: str, citations: str):
    """Saves a Q&A interaction to the database."""
    db = SessionLocal()
    try:
        log = ConversationLog(
            tenant_id=tenant_id,
            question=question,
            answer=answer,
            citations=citations,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

def get_all_logs():
    """Retrieves all conversation logs for the Admin Panel."""
    db = SessionLocal()
    try:
        # Join with Tenant table to show tenant names
        results = db.query(ConversationLog, Tenant.name).join(Tenant).all()
        
        logs_list = []
        for log, tenant_name in results:
            logs_list.append({
                "id": log.id, 
                "tenant_name": tenant_name,
                "question": log.question,
                "answer": log.answer,
                "timestamp": log.timestamp
            })
        return logs_list
    finally:
        db.close()
