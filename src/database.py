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

# --- CRITICAL FIX: Streamlit-safe writable DB path ---
DATABASE_URL = "sqlite:////tmp/app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """Creates all tables + seeds tenants."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("DB tables created.")
    except Exception as e:
        logger.exception(f"DB create failed: {e}")
        return

    db = SessionLocal()
    try:
        if db.query(Tenant).count() == 0:
            tenants = [
                Tenant(id="tenantA", name="Tenant Alpha Corp"),
                Tenant(id="tenantB", name="Tenant Beta Solutions"),
                Tenant(id="tenantC", name="Tenant Charlie Inc"),
                Tenant(id="admin", name="Admin Panel User")
            ]
            db.add_all(tenants)
            db.commit()
            logger.info("Initial tenants added.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Tenant init error: {e}")
    finally:
        db.close()


def log_conversation(tenant_id: str, question: str, answer: str, citations: str):
    db = SessionLocal()
    try:
        entry = ConversationLog(
            tenant_id=tenant_id,
            question=question,
            answer=answer,
            citations=citations,
            timestamp=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Log save error: {e}")
    finally:
        db.close()


def get_all_logs():
    db = SessionLocal()
    try:
        rows = (
            db.query(ConversationLog, Tenant.name)
            .join(Tenant, Tenant.id == ConversationLog.tenant_id)
            .order_by(ConversationLog.timestamp.desc())
            .all()
        )

        return [
            {
                "id": conv.id,
                "tenant_name": tenant_name,
                "question": conv.question,
                "answer": conv.answer,
                "citations": conv.citations,
                "timestamp": conv.timestamp,
            }
            for conv, tenant_name in rows
        ]
    except Exception as e:
        logger.exception(f"Log fetch error: {e}")
        return []
    finally:
        db.close()
