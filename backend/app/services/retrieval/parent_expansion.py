from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.database.models import DocumentChunkDB


@dataclass
class ExpandedContext:
    """
    Retrieved chunk enriched with its parent context.
    """

    chunk_id: int
    document_id: int

    text: str
    parent_text: str | None

    score: float
    rerank_score: float

    page_number: int | None
    section: str | None
    subsection: str | None

    chunk_level: str


def expand_parent_context(
    db: Session,
    chunk_id: int,
    text: str,
    score: float,
    rerank_score: float,
    page_number: int | None,
    section: str | None,
    subsection: str | None,
    chunk_level: str,
) -> ExpandedContext:
    """
    Expand a retrieved chunk with its parent chunk.

    The retrieved child remains the primary evidence.
    The parent provides additional surrounding context.

    If the retrieved chunk has no parent, the parent context
    is left as None.
    """

    chunk = (
        db.query(DocumentChunkDB)
        .filter(
            DocumentChunkDB.id == chunk_id
        )
        .first()
    )

    if chunk is None:
        raise ValueError(
            f"Chunk {chunk_id} not found."
        )

    parent_text = None

    if chunk.parent_chunk_id is not None:

        parent = (
            db.query(DocumentChunkDB)
            .filter(
                DocumentChunkDB.id
                == chunk.parent_chunk_id
            )
            .first()
        )

        if parent is not None:
            parent_text = parent.text

    return ExpandedContext(
        chunk_id=chunk_id,
        document_id=chunk.document_id,
        text=text,
        parent_text=parent_text,
        score=score,
        rerank_score=rerank_score,
        page_number=page_number,
        section=section,
        subsection=subsection,
        chunk_level=chunk_level,
    )
