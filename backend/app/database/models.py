from sqlalchemy import Column, String, Integer, Text, ForeignKey

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
    processing_status = Column(String, nullable=False, default="completed")
    user_id = Column(String, nullable=True, index=True)

class PaperDB(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    openalex_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)

class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True,)
    chunk_index = Column(Integer, nullable=False,)
    text = Column(Text, nullable=False,)
    character_count = Column(Integer, nullable=False,)


