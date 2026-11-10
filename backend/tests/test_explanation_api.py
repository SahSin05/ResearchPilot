from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.database.connection import get_db
from app.database.models import DocumentDB
from app.main import app

from app.services.embeddings import create_embedding_provider

from app.services.generation.explanation import ExplanationService
from app.services.retrieval.citations import (
    Citation,
    CitedContext,
)


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
        return 768

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * 767


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


def fake_collect_paper_evidence(
    db,
    document_id,
    embedding_provider,
):
    return [
        CitedContext(
            citation=Citation(
                citation_id=1,
                chunk_id=1,
                document_id=document_id,
                label="[C1]",
                page_number=1,
                section="Introduction",
                subsection=None,
            ),
            context_text=(
                "[C1]\n"
                "The paper studies a research problem."
            ),
        ),
    ]


def fake_explain(
    self,
    context,
):
    return {
        "problem": {
            "content": "The paper studies a research problem.",
            "citations": ["[C1]"],
        },
        "key_concepts": {
            "content": "The paper introduces important concepts.",
            "citations": ["[C1]"],
        },
        "methodology": {
            "content": "The authors evaluate their approach.",
            "citations": ["[C1]"],
        },
        "dataset": {
            "content": "The evidence describes the dataset.",
            "citations": ["[C1]"],
        },
        "results": {
            "content": "The evidence describes the reported results.",
            "citations": ["[C1]"],
        },
        "limitations": {
            "content": "The evidence describes limitations.",
            "citations": ["[C1]"],
        },
        "glossary": [
            {
                "term": "Research method",
                "definition": (
                    "The approach used to investigate "
                    "the research problem."
                ),
                "citations": ["[C1]"],
            }
        ],
    }


def test_explanation_api():
    db = TestingSessionLocal()

    document = DocumentDB(
        filename="explanation-api-test.txt",
        file_type="txt",
        file_size=100,
        page_count=1,
        extracted_text="Explanation API integration test.",
        file_path="uploads/explanation-api-test.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    import app.routes.explanation as explanation_route

    original_embedding_factory = (
        explanation_route.create_embedding_provider
    )

    original_evidence_collector = (
        explanation_route.collect_paper_evidence
    )

    original_explain = ExplanationService.explain

    try:
        explanation_route.create_embedding_provider = (
            lambda: FakeEmbeddingProvider()
        )

        explanation_route.collect_paper_evidence = (
            fake_collect_paper_evidence
        )

        ExplanationService.explain = fake_explain

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.get(
            f"/api/documents/{document.id}/explanation"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["problem"]["content"] == (
            "The paper studies a research problem."
        )

        assert data["problem"]["citations"] == ["[C1]"]

        assert data["methodology"]["content"] == (
            "The authors evaluate their approach."
        )

        assert len(data["glossary"]) == 1

        assert data["glossary"][0]["term"] == (
            "Research method"
        )

    finally:
        explanation_route.create_embedding_provider = (
            original_embedding_factory
        )

        explanation_route.collect_paper_evidence = (
            original_evidence_collector
        )

        ExplanationService.explain = original_explain

        app.dependency_overrides[get_db] = override_get_db

        db.delete(document)
        db.commit()
        db.close()