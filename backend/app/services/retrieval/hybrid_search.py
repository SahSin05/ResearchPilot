from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.embeddings.base import EmbeddingProvider
from app.services.retrieval.full_text_search import search_full_text
from app.services.retrieval.rrf import reciprocal_rank_fusion
from app.services.retrieval.simple_reranker import SimpleReranker
from app.services.retrieval.vector_search import search_similar_chunks


@dataclass
class HybridSearchResult:
    chunk_id: int
    document_id: int
    text: str
    score: float
    vector_score: float
    text_score: float
    rerank_score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str


def hybrid_search(
    db: Session,
    query: str,
    embedding_provider: EmbeddingProvider,
    top_k: int = 10,
    document_id: int | None = None,
) -> list[HybridSearchResult]:

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    vector_results = search_similar_chunks(
        db=db,
        query_embedding=embedding_provider.embed_query(query),
        top_k=top_k,
        document_id=document_id,
    )

    text_results = search_full_text(
        db=db,
        query_text=query,
        top_k=top_k,
        document_id=document_id,
    )

    vector_ranked_ids = [
        result.chunk_id
        for result in vector_results
    ]

    text_ranked_ids = [
        result.chunk_id
        for result in text_results
    ]

    fused_results = reciprocal_rank_fusion(
        ranked_lists=[
            vector_ranked_ids,
            text_ranked_ids,
        ]
    )

    vector_by_id = {
        result.chunk_id: result
        for result in vector_results
    }

    text_by_id = {
        result.chunk_id: result
        for result in text_results
    }

    candidate_documents = []

    for fused_result in fused_results:
        chunk_id = fused_result.chunk_id

        vector_result = vector_by_id.get(chunk_id)
        text_result = text_by_id.get(chunk_id)

        source = vector_result or text_result

        candidate_documents.append(
            (
                chunk_id,
                source.text,
            )
        )

    reranker = SimpleReranker()

    reranked_results = reranker.rerank(
        query=query,
        documents=candidate_documents,
    )

    source_by_id = {}

    for chunk_id in vector_by_id:
        source_by_id[chunk_id] = vector_by_id[chunk_id]

    for chunk_id in text_by_id:
        if chunk_id not in source_by_id:
            source_by_id[chunk_id] = text_by_id[chunk_id]

    vector_score_by_id = {
        result.chunk_id: result.score
        for result in vector_results
    }

    text_score_by_id = {
        result.chunk_id: result.score
        for result in text_results
    }

    results = []

    for reranked in reranked_results:

        source = source_by_id[reranked.chunk_id]

        results.append(
            HybridSearchResult(
                chunk_id=reranked.chunk_id,
                document_id=source.document_id,
                text=source.text,
                score=reranked.score,
                vector_score=vector_score_by_id.get(
                    reranked.chunk_id,
                    0.0,
                ),
                text_score=text_score_by_id.get(
                    reranked.chunk_id,
                    0.0,
                ),
                rerank_score=reranked.score,
                page_number=source.page_number,
                section=source.section,
                subsection=source.subsection,
                chunk_level=source.chunk_level,
            )
        )

    return results[:top_k]