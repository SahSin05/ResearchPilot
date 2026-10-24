from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import DocumentDB, DocumentChunkDB
from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.persistence import embed_pending_chunks


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
        return [0.001] * self.dimensions


def test_embed_pending_chunks():
    engine = create_engine(
        "postgresql+psycopg://researchpilot:researchpilot@localhost:5432/researchpilot"
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    document = DocumentDB(
        filename="embedding-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="ResearchPilot embedding persistence test.",
        file_path="uploads/embedding-test.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunkDB(
        document_id=document.id,
        chunk_index=0,
        chunk_level="child",
        text=(
            "Research papers contain scientific knowledge "
            "that can be retrieved using semantic search."
        ),
        character_count=90,
        content_hash="embedding-persistence-test",
        page_number=1,
        embedding_status="pending",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    try:
        provider = FakeEmbeddingProvider()

        processed = embed_pending_chunks(
            db=db,
            provider=provider,
            batch_size=1,
        )

        db.refresh(chunk)

        assert processed == 1
        assert chunk.embedding_status == "completed"
        assert chunk.embedding_model == "fake-embedding-model"
        assert chunk.embedding_version == "v1"
        assert chunk.embedding is not None
        assert len(chunk.embedding) == 1536

    finally:
        db.delete(chunk)
        db.delete(document)
        db.commit()
        db.close()