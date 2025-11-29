from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Tenant, Document, ConversationLog
from src.config import DATABASE_URL
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize Engine and Session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables and pre-populate initial tenants if they don't exist."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Pre-populate tenants for the demo
        if db.query(Tenant).count() == 0:
            db.add_all([
                Tenant(id="tenantA", name="Tenant Alpha Corp"),
                Tenant(id="tenantB", name="Tenant Beta Solutions"),
                # ADD THIS LINE:
                Tenant(id="tenantC", name="Tenant Charlie Inc"), 
                Tenant(id="admin", name="Admin Panel User")
            ])
            db.commit()
            logger.info("Initial tenants created.")
    except Exception as e:
        logger.exception(f"DB setup error: {e}")
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
        # results will be a list of tuples: (ConversationLog, tenant_name)
        results = db.query(ConversationLog, Tenant.name).join(Tenant).all()
        
        logs_list = []
        for log, tenant_name in results:
            logs_list.append({
                "id": log.id, # Corrected: Access 'id' directly on the ConversationLog object 'log'
                "tenant_name": tenant_name,
                "question": log.question,
                "answer": log.answer,
                "timestamp": log.timestamp
            })
        return logs_list
    finally:
        db.close()