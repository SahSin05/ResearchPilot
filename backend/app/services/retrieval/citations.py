from dataclasses import dataclass

from app.services.retrieval.context import ContextItem


@dataclass
class Citation:
    citation_id: int
    chunk_id: int
    document_id: int
    label: str
    page_number: int | None
    section: str | None
    subsection: str | None


@dataclass
class CitedContext:
    citation: Citation
    context_text: str


def build_citations(
    context_items: list[ContextItem],
) -> list[Citation]:
    citations: list[Citation] = []

    for index, item in enumerate(
        context_items,
        start=1,
    ):
        citations.append(
            Citation(
                citation_id=index,
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                label=f"[{index}]",
                page_number=item.page_number,
                section=item.section,
                subsection=item.subsection,
            )
        )

    return citations


def build_cited_context(
    context_items: list[ContextItem],
) -> list[CitedContext]:
    citations = build_citations(context_items)

    cited_context: list[CitedContext] = []

    for citation, item in zip(
        citations,
        context_items,
    ):
        cited_context.append(
            CitedContext(
                citation=citation,
                context_text=(
                    f"{citation.label}\n"
                    f"{item.context_text}"
                ),
            )
        )

    return cited_context