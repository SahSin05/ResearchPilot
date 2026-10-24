from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.retrieval.hybrid_search import (
    HybridSearchResult,
)
from app.services.retrieval.parent_expansion import (
    ExpandedContext,
    expand_parent_context,
)


@dataclass
class ContextItem:
    """
    Final context item prepared for downstream LLM generation.
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

    @property
    def context_text(self) -> str:
        """
        Return the text that should be supplied to the LLM.

        The retrieved child is placed first because it is the
        highest-confidence matching evidence. Parent context
        follows it as additional surrounding information.
        """

        if not self.parent_text:
            return self.text

        if self.parent_text.strip() == self.text.strip():
            return self.text

        return (
            f"{self.text}\n\n"
            f"Context:\n"
            f"{self.parent_text}"
        )


def select_context(
    db: Session,
    results: list[HybridSearchResult],
    max_items: int = 5,
    max_characters: int = 12000,
) -> list[ContextItem]:
    """
    Select and expand the best retrieved results.

    Selection is performed after hybrid retrieval and
    reranking.

    The function enforces both:
    - maximum number of context items
    - maximum total character budget
    """

    if max_items <= 0:
        raise ValueError(
            "max_items must be greater than zero."
        )

    if max_characters <= 0:
        raise ValueError(
            "max_characters must be greater than zero."
        )

    selected: list[ContextItem] = []

    seen_chunks: set[int] = set()

    total_characters = 0

    for result in results:

        if len(selected) >= max_items:
            break

        if result.chunk_id in seen_chunks:
            continue

        expanded: ExpandedContext = (
            expand_parent_context(
                db=db,
                chunk_id=result.chunk_id,
                text=result.text,
                score=result.score,
                rerank_score=result.rerank_score,
                page_number=result.page_number,
                section=result.section,
                subsection=result.subsection,
                chunk_level=result.chunk_level,
            )
        )

        item = ContextItem(
            chunk_id=expanded.chunk_id,
            document_id=expanded.document_id,
            text=expanded.text,
            parent_text=expanded.parent_text,
            score=expanded.score,
            rerank_score=expanded.rerank_score,
            page_number=expanded.page_number,
            section=expanded.section,
            subsection=expanded.subsection,
            chunk_level=expanded.chunk_level,
        )

        item_size = len(
            item.context_text
        )

        if (
            total_characters + item_size
            > max_characters
        ):
            continue

        selected.append(item)

        seen_chunks.add(
            result.chunk_id
        )

        total_characters += item_size

    return selected
