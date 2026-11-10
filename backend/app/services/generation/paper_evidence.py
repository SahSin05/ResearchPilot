from sqlalchemy.orm import Session

from app.services.embeddings.base import EmbeddingProvider
from app.services.retrieval.citations import (
    CitedContext,
    build_cited_context,
)
from app.services.retrieval.context import (
    ContextItem,
    select_context,
)
from app.services.retrieval.hybrid_search import (
    hybrid_search,
)


EXPLANATION_QUERIES = (
    "What problem or research question does this paper address?",
    "What are the key concepts and main contribution of this paper?",
    "What methodology or approach does the paper use?",
    "What dataset, benchmark, corpus, or experimental data does the paper use?",
    "What experimental results, evaluation results, findings, comparisons, or performance does the paper report?",
    "What limitations, weaknesses, shortcomings, constraints, or future work does the paper discuss?",
)


def collect_paper_evidence(
    db: Session,
    document_id: int,
    embedding_provider: EmbeddingProvider,
    max_items: int = 8,
    max_characters: int = 12000,
) -> list[CitedContext]:
    """
    Collect balanced, section-aware evidence for a structured
    paper explanation.

    Each explanation topic receives its own retrieval budget so that
    evidence for one section cannot completely crowd out evidence
    needed by another section.
    """

    if document_id <= 0:
        raise ValueError(
            "document_id must be greater than zero."
        )

    if max_items <= 0:
        raise ValueError(
            "max_items must be greater than zero."
        )

    if max_characters <= 0:
        raise ValueError(
            "max_characters must be greater than zero."
        )

    retrieved_results = []

    seen_chunk_ids: set[int] = set()

    # Give every explanation topic an opportunity to contribute
    # evidence instead of allowing the strongest topic to dominate.
    results_per_query = max(
        1,
        max_items // len(EXPLANATION_QUERIES),
    )

    # The remainder is distributed to the first few queries.
    remainder = max_items % len(EXPLANATION_QUERIES)

    for index, query in enumerate(EXPLANATION_QUERIES):
        query_budget = results_per_query

        if index < remainder:
            query_budget += 1

        results = hybrid_search(
            db=db,
            query=query,
            embedding_provider=embedding_provider,
            top_k=5,
            document_id=document_id,
        )

        query_selected = 0

        for result in results:
            if result.chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(result.chunk_id)
            retrieved_results.append(result)

            query_selected += 1

            if query_selected >= query_budget:
                break

    if not retrieved_results:
        return []

    # Keep the strongest candidates first while preserving the
    # per-query diversity established above.
    retrieved_results.sort(
        key=lambda result: result.rerank_score,
        reverse=True,
    )

    context_items: list[ContextItem] = select_context(
        db=db,
        results=retrieved_results,
        max_items=max_items,
        max_characters=max_characters,
    )

    return build_cited_context(
        context_items,
    )