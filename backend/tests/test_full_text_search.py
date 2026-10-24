from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import DocumentDB, DocumentChunkDB
from app.services.retrieval.full_text_search import search_full_text


DATABASE_URL = (
    "postgresql+psycopg://researchpilot:researchpilot"
    "@localhost:5432/researchpilot"
)


def test_full_text_search():
    engine = create_engine(DATABASE_URL)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    document = DocumentDB(
        filename="fts-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="Full text search integration test.",
        file_path="uploads/fts-test.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    matching_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=0,
        chunk_level="child",
        text=(
            "PostgreSQL full text search provides "
            "powerful keyword retrieval."
        ),
        character_count=72,
        content_hash="fts-matching",
        page_number=3,
        section="Methods",
        embedding_status="completed",
    )

    unrelated_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=1,
        chunk_level="child",
        text=(
            "The experiment measured temperature "
            "and pressure over time."
        ),
        character_count=65,
        content_hash="fts-unrelated",
        page_number=4,
        section="Results",
        embedding_status="completed",
    )

    db.add_all([
        matching_chunk,
        unrelated_chunk,
    ])
    db.commit()

    try:
        results = search_full_text(
            db=db,
            query_text="PostgreSQL full text search",
            top_k=5,
        )

        assert len(results) >= 1

        assert results[0].chunk_id == matching_chunk.id
        assert results[0].text == (
            "PostgreSQL full text search provides "
            "powerful keyword retrieval."
        )

        assert results[0].score > 0

    finally:
        db.delete(matching_chunk)
        db.delete(unrelated_chunk)
        db.delete(document)
        db.commit()
        db.close()