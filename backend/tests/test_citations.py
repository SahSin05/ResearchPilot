from app.services.retrieval.citations import (
    build_citations,
    build_cited_context,
)
from app.services.retrieval.context import ContextItem


def create_context_item(
    chunk_id: int,
    page_number: int | None = 1,
    section: str | None = "Retrieval",
    subsection: str | None = "Hybrid Search",
) -> ContextItem:
    return ContextItem(
        chunk_id=chunk_id,
        document_id=10,
        text=f"Relevant text for chunk {chunk_id}.",
        parent_text="Parent context.",
        score=0.95,
        rerank_score=0.90,
        page_number=page_number,
        section=section,
        subsection=subsection,
        chunk_level="child",
    )


def test_build_citations_assigns_sequential_ids():
    context_items = [
        create_context_item(1),
        create_context_item(2),
        create_context_item(3),
    ]

    citations = build_citations(
        context_items
    )

    assert len(citations) == 3

    assert citations[0].citation_id == 1
    assert citations[0].label == "[1]"

    assert citations[1].citation_id == 2
    assert citations[1].label == "[2]"

    assert citations[2].citation_id == 3
    assert citations[2].label == "[3]"


def test_build_citations_preserves_source_metadata():
    context_items = [
        create_context_item(
            chunk_id=42,
            page_number=7,
            section="Methods",
            subsection="Data Collection",
        )
    ]

    citations = build_citations(
        context_items
    )

    citation = citations[0]

    assert citation.citation_id == 1
    assert citation.chunk_id == 42
    assert citation.document_id == 10
    assert citation.label == "[1]"
    assert citation.page_number == 7
    assert citation.section == "Methods"
    assert citation.subsection == "Data Collection"


def test_build_citations_handles_missing_metadata():
    context_items = [
        create_context_item(
            chunk_id=50,
            page_number=None,
            section=None,
            subsection=None,
        )
    ]

    citations = build_citations(
        context_items
    )

    citation = citations[0]

    assert citation.chunk_id == 50
    assert citation.page_number is None
    assert citation.section is None
    assert citation.subsection is None


def test_build_cited_context_adds_citation_label():
    context_items = [
        create_context_item(1),
        create_context_item(2),
    ]

    cited_context = build_cited_context(
        context_items
    )

    assert len(cited_context) == 2

    assert (
        cited_context[0].context_text.startswith(
            "[1]\n"
        )
    )

    assert (
        "Relevant text for chunk 1."
        in cited_context[0].context_text
    )

    assert (
        cited_context[1].context_text.startswith(
            "[2]\n"
        )
    )


def test_build_citations_empty_context():
    citations = build_citations([])

    assert citations == []


def test_build_cited_context_empty_context():
    cited_context = build_cited_context([])

    assert cited_context == []