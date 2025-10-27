"""This file contains the thread model for the application."""

from datetime import datetime

from pgvector.sqlalchemy import Vector as PGVector
from sqlalchemy import Column
from sqlmodel import (
    Field,
    SQLModel,
)

EMBEDDING_DIM = 1536
class FileObject(SQLModel, table=True):
    __tablename__ = "file_objects"

    id: str = Field(primary_key=True)
    file_name: str = Field(default="")
    description: str = Field(default="")
    created_by: str
    vector:  list[float] = Field(sa_column=Column(PGVector(EMBEDDING_DIM)))
    session_id: str
    file_type: str = Field(default="")
    s3_key: str
    s3_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FileChunk(SQLModel, table=True):
    __tablename__ = "file_chunks "
    id: str = Field(primary_key=True)
    file_id: str = Field(default="")
    embedding:  list[float] = Field(sa_column=Column(PGVector(EMBEDDING_DIM)))
    content: str
    chunk_index: int



#file_chunks (id, file_id, chunk_index, content, embedding)
