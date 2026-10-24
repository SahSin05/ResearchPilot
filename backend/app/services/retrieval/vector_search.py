from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.database.models import DocumentChunkDB


@dataclass
class VectorSearchResult:
    chunk_id: int
    document_id: int
    text: str
    score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str


def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    top_k: int = 5,
    document_id: int | None = None,
) -> list[VectorSearchResult]:
    """
    Search completed document chunks by cosine similarity.
    """

    if not query_embedding:
        raise ValueError("Query embedding cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    query = (
        db.query(
            DocumentChunkDB,
            DocumentChunkDB.embedding.cosine_distance(
                query_embedding
            ).label("distance"),
        )
        .filter(
            DocumentChunkDB.embedding_status == "completed",
            DocumentChunkDB.embedding.is_not(None),
        )
    )

    if document_id is not None:
        query = query.filter(
            DocumentChunkDB.document_id == document_id
        )

    rows = (
        query
        .order_by("distance")
        .limit(top_k)
        .all()
    )

    results = []

    for chunk, distance in rows:
        score = 1.0 - float(distance)

        results.append(
            VectorSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                text=chunk.text,
                score=score,
                page_number=chunk.page_number,
                section=chunk.section,
                subsection=chunk.subsection,
                chunk_level=chunk.chunk_level,
            )
        )

    return results