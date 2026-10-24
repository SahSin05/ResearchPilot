from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import DocumentDB, DocumentChunkDB
from app.services.embeddings.base import EmbeddingProvider
from app.services.retrieval.service import retrieve_relevant_chunks


DATABASE_URL = (
    "postgresql+psycopg://researchpilot:researchpilot"
    "@localhost:5432/researchpilot"
)


class FakeEmbeddingProvider(EmbeddingProvider):

    @property
    def model_name(self) -> str:
        return "fake-embedding-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [0.001] * self.dimensions
            for _ in texts
        ]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return [1.0] + [0.0] * 1535


def test_retrieve_relevant_chunks():
    engine = create_engine(DATABASE_URL)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    document = DocumentDB(
        filename="retrieval-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="Retrieval service integration test.",
        file_path="uploads/retrieval-test.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    relevant_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=0,
        chunk_level="child",
        text="This chunk is highly relevant to the query.",
        character_count=45,
        content_hash="retrieval-relevant",
        page_number=1,
        embedding=[1.0] + [0.0] * 1535,
        embedding_model="fake-embedding-model",
        embedding_version="v1",
        embedding_status="completed",
    )

    unrelated_chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=1,
        chunk_level="child",
        text="This chunk contains unrelated information.",
        character_count=43,
        content_hash="retrieval-unrelated",
        page_number=1,
        embedding=[0.0, 1.0] + [0.0] * 1534,
        embedding_model="fake-embedding-model",
        embedding_version="v1",
        embedding_status="completed",
    )

    db.add_all([
        relevant_chunk,
        unrelated_chunk,
    ])
    db.commit()

    try:
        provider = FakeEmbeddingProvider()

        results = retrieve_relevant_chunks(
            db=db,
            query="What information is relevant?",
            embedding_provider=provider,
            top_k=2,
        )

        assert len(results) == 2

        assert results[0].chunk_id == relevant_chunk.id
        assert results[0].text == (
            "This chunk is highly relevant to the query."
        )

        assert results[0].score > results[1].score

    finally:
        db.delete(relevant_chunk)
        db.delete(unrelated_chunk)
        db.delete(document)
        db.commit()
        db.close()