from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    file_name = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    vector_count = Column(Integer, default=0)

class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citations = Column(Text)
    is_validated = Column(Integer, default=0)
