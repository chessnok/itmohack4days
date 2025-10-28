"""This file contains the thread model for the application."""

from datetime import datetime

from pgvector.sqlalchemy import Vector as PGVector
from sqlalchemy import Column
from sqlmodel import (
    Field,
    SQLModel,
)

from app.core.config import settings


class FileObject(SQLModel, table=True):
    __tablename__ = "file_objects"

    id: str = Field(primary_key=True)
    file_name: str = Field(default="")
    description: str = Field(default="")
    created_by: str
    embedding:  list[float] = Field(sa_column=Column(PGVector(settings.EMBEDDING_DIM)))
    session_id: str
    file_type: str = Field(default="")
    s3_key: str
    s3_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FileChunk(SQLModel, table=True):
    __tablename__ = "file_chunks"
    id: str = Field(primary_key=True)
    file_id: str = Field(default="")
    embedding:  list[float] = Field(sa_column=Column(PGVector(settings.EMBEDDING_DIM)))
    content: str = Field(default="")
    chunk_index: int

