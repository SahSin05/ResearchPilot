from types import SimpleNamespace

from app.services.generation.paper_evidence import (
    EXPLANATION_QUERIES,
    collect_paper_evidence,
)


class FakeEmbeddingProvider:
    @property
    def dimensions(self) -> int:
        return 768

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * 767


def test_collect_paper_evidence_uses_targeted_queries_and_deduplicates(
    monkeypatch,
):
    calls = []

    def fake_hybrid_search(
        db,
        query,
        embedding_provider,
        top_k,
        document_id,
    ):
        calls.append(
            {
                "query": query,
                "top_k": top_k,
                "document_id": document_id,
            }
        )

        query_index = EXPLANATION_QUERIES.index(query)

        return [
            SimpleNamespace(
                chunk_id=query_index + 1,
                document_id=document_id,
                text=f"Evidence for query {query_index}",
                score=1.0,
                vector_score=1.0,
                text_score=1.0,
                rerank_score=1.0 - (query_index * 0.01),
                page_number=query_index + 1,
                section=f"Section {query_index + 1}",
                subsection=None,
                chunk_level="child",
            ),
            SimpleNamespace(
                chunk_id=999,
                document_id=document_id,
                text="Shared evidence",
                score=0.5,
                vector_score=0.5,
                text_score=0.5,
                rerank_score=0.5,
                page_number=99,
                section="Shared",
                subsection=None,
                chunk_level="child",
            ),
        ]

    def fake_select_context(
        db,
        results,
        max_items,
        max_characters,
    ):
        assert len(results) == len(EXPLANATION_QUERIES) + 1
        assert max_items == 8
        assert max_characters == 12000

        return [
            SimpleNamespace(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                text=result.text,
                parent_text=None,
                score=result.score,
                rerank_score=result.rerank_score,
                page_number=result.page_number,
                section=result.section,
                subsection=result.subsection,
                chunk_level=result.chunk_level,
                context_text=result.text,
            )
            for result in results
        ]

    monkeypatch.setattr(
        "app.services.generation.paper_evidence.hybrid_search",
        fake_hybrid_search,
    )

    monkeypatch.setattr(
        "app.services.generation.paper_evidence.select_context",
        fake_select_context,
    )

    evidence = collect_paper_evidence(
        db=object(),
        document_id=42,
        embedding_provider=FakeEmbeddingProvider(),
    )

    assert len(calls) == 6

    assert [call["query"] for call in calls] == list(
        EXPLANATION_QUERIES
    )

    assert all(
        call["top_k"] == 5
        for call in calls
    )

    assert all(
        call["document_id"] == 42
        for call in calls
    )

    assert len(evidence) == 7

    labels = [
        item.citation.label
        for item in evidence
    ]

    assert labels == [
        "[C1]",
        "[C2]",
        "[C3]",
        "[C4]",
        "[C5]",
        "[C6]",
        "[C7]",
    ]

    chunk_ids = [
        item.citation.chunk_id
        for item in evidence
    ]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_collect_paper_evidence_rejects_invalid_document_id():
    try:
        collect_paper_evidence(
            db=object(),
            document_id=0,
            embedding_provider=FakeEmbeddingProvider(),
        )
    except ValueError as exc:
        assert str(exc) == "document_id must be greater than zero."
    else:
        raise AssertionError("Expected ValueError")


def test_collect_paper_evidence_returns_empty_when_nothing_is_retrieved(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.services.generation.paper_evidence.hybrid_search",
        lambda **kwargs: [],
    )

    result = collect_paper_evidence(
        db=object(),
        document_id=42,
        embedding_provider=FakeEmbeddingProvider(),
    )

    assert result == []