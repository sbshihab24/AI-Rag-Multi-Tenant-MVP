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

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.models import Base, Tenant, Document, ConversationLog

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# ✔ STREAMLIT-SAFE DATABASE LOCATION
# DO NOT STORE DB INSIDE REPO (read-only)
# /tmp/ is always writable on Streamlit Cloud
# ─────────────────────────────────────────────
DATABASE_URL = "sqlite:////tmp/app.db"

# Create engine with thread-safe config for Streamlit
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # REQUIRED for Streamlit
    echo=False
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# SQLAlchemy Base (models attach to this)
Base = declarative_base()

# ─────────────────────────────────────────────
# DB INITIALIZATION
# ─────────────────────────────────────────────
def init_db():
    """Create tables and pre-populate tenants."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")
    except Exception as e:
        logger.exception(f"Failed to create DB tables: {e}")
        return

    db = SessionLocal()
    try:
        # Only seed if empty
        if db.query(Tenant).count() == 0:
            tenants = [
                Tenant(id="tenantA", name="Tenant Alpha Corp"),
                Tenant(id="tenantB", name="Tenant Beta Solutions"),
                Tenant(id="tenantC", name="Tenant Charlie Inc"),
                Tenant(id="admin", name="Admin Panel User")
            ]
            db.add_all(tenants)
            db.commit()
            logger.info("Initial tenants created.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Tenant initialization error: {e}")
    finally:
        db.close()


# ─────────────────────────────────────────────
# LOGGING CONVERSATIONS
# ─────────────────────────────────────────────
def log_conversation(tenant_id: str, question: str, answer: str, citations: str):
    """Save Q&A interaction to DB."""
    db = SessionLocal()
    try:
        entry = ConversationLog(
            tenant_id=tenant_id,
            question=question,
            answer=answer,
            citations=citations,
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Error logging conversation: {e}")
    finally:
        db.close()


# ─────────────────────────────────────────────
# FETCH ALL LOGS FOR ADMIN PANEL
# ─────────────────────────────────────────────
def get_all_logs():
    db = SessionLocal()
    try:
        # Join tenant table to display tenant names
        rows = (
            db.query(ConversationLog, Tenant.name)
            .join(Tenant, Tenant.id == ConversationLog.tenant_id)
            .order_by(ConversationLog.timestamp.desc())
            .all()
        )

        logs = []
        for log, tenant_name in rows:
            logs.append({
                "id": log.id,
                "tenant_name": tenant_name,
                "question": log.question,
                "answer": log.answer,
                "citations": log.citations,
                "timestamp": log.timestamp,
            })
        return logs
    except Exception as e:
        logger.exception(f"Error fetching logs: {e}")
        return []
    finally:
        db.close()

      