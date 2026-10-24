from app.services.retrieval.simple_reranker import (
    SimpleReranker,
)


def test_simple_reranker_prefers_term_overlap():

    reranker = SimpleReranker()

    results = reranker.rerank(
        query="transformer attention mechanism",
        documents=[
            (
                1,
                "This paper discusses database indexing.",
            ),
            (
                2,
                "The transformer uses an attention mechanism.",
            ),
            (
                3,
                "Attention mechanisms are important in transformers.",
            ),
        ],
    )

    assert results[0].chunk_id in [2, 3]

    assert results[0].score > results[-1].score


def test_simple_reranker_handles_empty_documents():

    reranker = SimpleReranker()

    results = reranker.rerank(
        query="attention",
        documents=[
            (1, ""),
        ],
    )

    assert results[0].chunk_id == 1
    assert results[0].score == 0.0