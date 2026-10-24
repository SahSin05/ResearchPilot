from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import DocumentDB, DocumentChunkDB
from app.services.retrieval.vector_search import search_similar_chunks


DATABASE_URL = (
    "postgresql+psycopg://researchpilot:researchpilot"
    "@localhost:5432/researchpilot"
)


def test_vector_similarity_search():
    engine = create_engine(DATABASE_URL)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    document = DocumentDB(
        filename="vector-search-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="Vector search integration test.",
        file_path="uploads/vector-search-test.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    similar_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=0,
        chunk_level="child",
        text="This chunk is semantically similar.",
        character_count=40,
        content_hash="vector-search-similar",
        page_number=1,
        embedding=[1.0] + [0.0] * 1535,
        embedding_model="fake-embedding-model",
        embedding_version="v1",
        embedding_status="completed",
    )

    different_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=1,
        chunk_level="child",
        text="This chunk is semantically different.",
        character_count=41,
        content_hash="vector-search-different",
        page_number=1,
        embedding=[0.0, 1.0] + [0.0] * 1534,
        embedding_model="fake-embedding-model",
        embedding_version="v1",
        embedding_status="completed",
    )

    db.add_all([
        similar_chunk,
        different_chunk,
    ])
    db.commit()

    try:
        query_embedding = [1.0] + [0.0] * 1535

        results = search_similar_chunks(
            db=db,
            query_embedding=query_embedding,
            top_k=2,
        )

        assert len(results) == 2

        assert results[0].chunk_id == similar_chunk.id
        assert results[0].text == (
            "This chunk is semantically similar."
        )

        assert results[0].score > results[1].score

    finally:
        db.delete(similar_chunk)
        db.delete(different_chunk)
        db.delete(document)
        db.commit()
        db.close()