from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import DocumentChunkDB


@dataclass
class FullTextSearchResult:
    chunk_id: int
    document_id: int
    text: str
    score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str


def search_full_text(
    db: Session,
    query_text: str,
    top_k: int = 5,
    document_id: int | None = None,
) -> list[FullTextSearchResult]:
    """
    Search document chunks using PostgreSQL full-text search.
    """

    if not query_text.strip():
        raise ValueError("Query text cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    search_vector = func.to_tsvector(
        "english",
        DocumentChunkDB.text,
    )

    search_query = func.plainto_tsquery(
        "english",
        query_text,
    )

    rank = func.ts_rank_cd(
        search_vector,
        search_query,
    )

    query = (
        db.query(
            DocumentChunkDB,
            rank.label("rank"),
        )
        .filter(
            DocumentChunkDB.embedding_status == "completed",
            search_vector.op("@@")(search_query),
        )
    )

    if document_id is not None:
        query = query.filter(
            DocumentChunkDB.document_id == document_id
        )

    rows = (
        query
        .order_by(rank.desc())
        .limit(top_k)
        .all()
    )

    results = []

    for chunk, score in rows:
        results.append(
            FullTextSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                text=chunk.text,
                score=float(score),
                page_number=chunk.page_number,
                section=chunk.section,
                subsection=chunk.subsection,
                chunk_level=chunk.chunk_level,
            )
        )

    return results