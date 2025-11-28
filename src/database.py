# src/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Tenant, Document, ConversationLog
from src.config import DATABASE_URL
from datetime import datetime

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
        logs = db.query(ConversationLog, Tenant.name).join(Tenant).all()
        return [{"id": log.ConversationLog.id, 
                 "tenant_name": tenant_name,
                 "question": log.ConversationLog.question,
                 "answer": log.ConversationLog.answer,
                 "timestamp": log.ConversationLog.timestamp} 
                for log, tenant_name in logs]
    finally:
        db.close()