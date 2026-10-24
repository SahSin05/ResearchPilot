from types import SimpleNamespace

from app.services.retrieval import hybrid_search as hybrid_module


class FakeEmbeddingProvider:
    def embed_query(self, text: str):
        return [1.0]

    @property
    def dimensions(self):
        return 1

    @property
    def model_name(self):
        return "fake"


def test_hybrid_search_combines_vector_and_text_results(monkeypatch):

    vector_results = [
        SimpleNamespace(
            chunk_id=1,
            document_id=1,
            text="Vector result",
            score=0.9,
            page_number=1,
            section="Introduction",
            subsection=None,
            chunk_level="child",
        ),
        SimpleNamespace(
            chunk_id=2,
            document_id=1,
            text="Second vector result",
            score=0.7,
            page_number=2,
            section="Methods",
            subsection=None,
            chunk_level="child",
        ),
    ]

    text_results = [
        SimpleNamespace(
            chunk_id=2,
            document_id=1,
            text="Second vector result",
            score=0.8,
            page_number=2,
            section="Methods",
            subsection=None,
            chunk_level="child",
        ),
        SimpleNamespace(
            chunk_id=3,
            document_id=1,
            text="Text-only result",
            score=0.6,
            page_number=3,
            section="Results",
            subsection=None,
            chunk_level="child",
        ),
    ]

    monkeypatch.setattr(
        hybrid_module,
        "search_similar_chunks",
        lambda **kwargs: vector_results,
    )

    monkeypatch.setattr(
        hybrid_module,
        "search_full_text",
        lambda **kwargs: text_results,
    )

    results = hybrid_module.hybrid_search(
        db=None,
        query="test query",
        embedding_provider=FakeEmbeddingProvider(),
        top_k=10,
    )

    assert len(results) == 3

    assert results[0].chunk_id == 2
    assert results[0].vector_score == 0.7
    assert results[0].text_score == 0.8

    assert results[1].chunk_id == 1
    assert results[2].chunk_id == 3