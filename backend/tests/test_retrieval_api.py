from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import DocumentDB, DocumentChunkDB
from app.database.connection import get_db
from app.main import app
from app.services.embeddings import create_embedding_provider


DATABASE_URL = (
    "postgresql+psycopg://researchpilot:researchpilot"
    "@localhost:5432/researchpilot"
)


class FakeEmbeddingProvider:
    @property
    def model_name(self) -> str:
        return "fake-embedding-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * 1535


engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_retrieval_api():
    db = TestingSessionLocal()

    document = DocumentDB(
        filename="retrieval-api-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="Retrieval API integration test.",
        file_path="uploads/retrieval-api-test.txt",
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
        text="This chunk is relevant to the research question.",
        character_count=48,
        content_hash="retrieval-api-relevant",
        page_number=2,
        section="Methods",
        subsection="Data Collection",
        embedding=[1.0] + [0.0] * 1535,
        embedding_model="fake-embedding-model",
        embedding_version="v1",
        embedding_status="completed",
    )

    db.add(relevant_chunk)
    db.commit()
    db.refresh(relevant_chunk)

    original_factory = create_embedding_provider

    try:
        import app.routes.retrieval as retrieval_route

        retrieval_route.create_embedding_provider = (
            lambda: FakeEmbeddingProvider()
        )

        client = TestClient(app)

        response = client.post(
            "/api/retrieval/search",
            json={
                "query": "What is the research question?",
                "top_k": 5,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "results" in data
        assert len(data["results"]) >= 1

        result = data["results"][0]

        assert result["chunk_id"] == relevant_chunk.id
        assert result["document_id"] == document.id
        assert result["text"] == (
            "This chunk is relevant to the research question."
        )
        assert result["page_number"] == 2
        assert result["section"] == "Methods"
        assert result["subsection"] == "Data Collection"

    finally:
        retrieval_route.create_embedding_provider = original_factory

        db.delete(relevant_chunk)
        db.delete(document)
        db.commit()
        db.close()