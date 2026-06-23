from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Integer, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import func
import uuid
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id   = Column(String(255), unique=True, nullable=False)
    email      = Column(String(255), nullable=False)
    full_name  = Column(String(255))
    currency   = Column(String(3), default="AED")
    region     = Column(String(10), default="UAE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Statement(Base):
    __tablename__ = "statements"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), nullable=False)
    file_name  = Column(String(500), nullable=False)
    file_url   = Column(Text, nullable=False)
    file_type  = Column(String(10), nullable=False)
    status     = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    statement_id        = Column(UUID(as_uuid=True), nullable=False)
    user_id             = Column(UUID(as_uuid=True), nullable=False)
    date                = Column(String(20), nullable=False)
    merchant            = Column(String(500))
    amount              = Column(Float, nullable=False)
    currency            = Column(String(3), nullable=False)
    type                = Column(String(10), nullable=False)
    description         = Column(Text)
    category            = Column(String(50))
    category_confidence = Column(Float)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

class FinancialReport(Base):
    __tablename__ = "financial_reports"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), nullable=False)
    statement_id = Column(UUID(as_uuid=True), nullable=False)
    report_data  = Column(JSONB, nullable=False)
    waste_score  = Column(Integer)
    savings_score = Column(Integer)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
