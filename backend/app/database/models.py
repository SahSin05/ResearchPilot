from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from app.database.connection import Base


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=True)
    extracted_text = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    processing_status = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )
    user_id = Column(String, nullable=True, index=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class PaperDB(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    openalex_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)


class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_chunk_id = Column(
        Integer,
        ForeignKey("document_chunks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False)
    chunk_level = Column(
        String,
        nullable=False,
        default="child",
    )

    text = Column(Text, nullable=False)
    character_count = Column(Integer, nullable=False)

    content_hash = Column(
        String(64),
        nullable=False,
        index=True,
    )

    page_number = Column(
        Integer,
        nullable=True,
        index=True,
    )

    section = Column(String, nullable=True)
    subsection = Column(String, nullable=True)

    embedding = Column(
        Vector(1536),
        nullable=True,
    )

    embedding_model = Column(String, nullable=True)
    embedding_version = Column(String, nullable=True)

    embedding_status = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
        Index(
            "ix_document_chunks_document_parent",
            "document_id",
            "parent_chunk_id",
        ),
        Index(
            "ix_document_chunks_document_page",
            "document_id",
            "page_number",
        ),
    )
    