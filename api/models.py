from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text

from api.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    question = Column(Text, nullable=False)
    final_sql = Column(Text, nullable=True)
    success = Column(Boolean, default=False)
    iterations = Column(Integer, default=1)
    latency_ms = Column(Float, nullable=True)
    error_trace = Column(Text, nullable=True)
    semantic_score = Column(Float, nullable=True)
    schema_version = Column(String, default="v1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    query_history_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)
    rating = Column(String, nullable=False)  # "up" or "down"
    corrected_sql = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SchemaEmbedding(Base):
    __tablename__ = "schema_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    schema_version = Column(String(20), nullable=False, default="v1")
    entry_type = Column(String(20), nullable=False)
    database_name = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100))
    data_type = Column(String(50))
    description = Column(Text)
    sample_values = Column(JSON)
    fk_references = Column(String(300))
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
