from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.embeddings.base import EmbeddingProvider
from app.services.retrieval.vector_search import (
    VectorSearchResult,
    search_similar_chunks,
)


@dataclass
class RetrievalResult:
    chunk_id: int
    document_id: int
    text: str
    score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str


def retrieve_relevant_chunks(
    db: Session,
    query: str,
    embedding_provider: EmbeddingProvider,
    top_k: int = 5,
    document_id: int | None = None,
) -> list[RetrievalResult]:
    """
    Convert a user query into an embedding and retrieve
    the most semantically similar document chunks.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    query_embedding = embedding_provider.embed_query(query)

    vector_results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
    )

    return [
        RetrievalResult(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            text=result.text,
            score=result.score,
            page_number=result.page_number,
            section=result.section,
            subsection=result.subsection,
            chunk_level=result.chunk_level,
        )
        for result in vector_results
    ]