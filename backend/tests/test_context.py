from dataclasses import dataclass

from app.database.connection import SessionLocal
from app.database.models import (
    DocumentChunkDB,
    DocumentDB,
)
from app.services.retrieval.context import (
    select_context,
)
from app.services.retrieval.parent_expansion import (
    expand_parent_context,
)


@dataclass
class FakeHybridResult:
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


def create_test_hierarchy(db):
    """
    Create a small parent/child hierarchy directly in
    PostgreSQL for context-expansion tests.
    """

    document = DocumentDB(
        filename="context-test.txt",
        file_type="text/plain",
        file_size=100,
        page_count=1,
        extracted_text=(
            "Parent context for ResearchPilot."
        ),
        file_path="test-context.txt",
        processing_status="completed",
        user_id="test-user",
    )

    db.add(document)
    db.flush()

    parent = DocumentChunkDB(
        document_id=document.id,
        chunk_index=0,
        chunk_level="parent",
        parent_chunk_id=None,
        text=(
            "ResearchPilot uses hybrid retrieval. "
            "It combines semantic vector search with "
            "PostgreSQL full-text search."
        ),
        character_count=120,
        content_hash="parent-context-hash",
        page_number=1,
        section="Retrieval",
        subsection="Hybrid Search",
        embedding_status="completed",
    )

    db.add(parent)
    db.flush()

    child = DocumentChunkDB(
        document_id=document.id,
        chunk_index=1,
        chunk_level="child",
        parent_chunk_id=parent.id,
        text=(
            "Hybrid retrieval combines vector search "
            "and full-text search."
        ),
        character_count=70,
        content_hash="child-context-hash",
        page_number=1,
        section="Retrieval",
        subsection="Hybrid Search",
        embedding_status="completed",
    )

    db.add(child)
    db.commit()
    db.refresh(document)
    db.refresh(parent)
    db.refresh(child)

    return document, parent, child


def cleanup_test_hierarchy(
    db,
    document_id: int,
):
    chunks = (
        db.query(DocumentChunkDB)
        .filter(
            DocumentChunkDB.document_id
            == document_id
        )
        .all()
    )

    for chunk in chunks:
        db.delete(chunk)

    document = (
        db.query(DocumentDB)
        .filter(
            DocumentDB.id == document_id
        )
        .first()
    )

    if document:
        db.delete(document)

    db.commit()


def test_expand_parent_context():
    db = SessionLocal()

    document = None

    try:
        (
            document,
            parent,
            child,
        ) = create_test_hierarchy(db)

        expanded = expand_parent_context(
            db=db,
            chunk_id=child.id,
            text=child.text,
            score=0.95,
            rerank_score=0.90,
            page_number=child.page_number,
            section=child.section,
            subsection=child.subsection,
            chunk_level=child.chunk_level,
        )

        assert expanded.chunk_id == child.id
        assert (
            expanded.document_id
            == document.id
        )

        assert expanded.text == child.text

        assert (
            expanded.parent_text
            == parent.text
        )

        assert expanded.score == 0.95
        assert expanded.rerank_score == 0.90

        assert (
            expanded.page_number
            == child.page_number
        )

        assert (
            expanded.section
            == child.section
        )

        assert (
            expanded.subsection
            == child.subsection
        )

    finally:
        if document is not None:
            cleanup_test_hierarchy(
                db,
                document.id,
            )

        db.close()


def test_select_context_expands_parent():
    db = SessionLocal()

    document = None

    try:
        (
            document,
            parent,
            child,
        ) = create_test_hierarchy(db)

        result = FakeHybridResult(
            chunk_id=child.id,
            document_id=document.id,
            text=child.text,
            score=0.95,
            vector_score=0.94,
            text_score=0.90,
            rerank_score=0.95,
            page_number=1,
            section="Retrieval",
            subsection="Hybrid Search",
            chunk_level="child",
        )

        selected = select_context(
            db=db,
            results=[result],
            max_items=5,
            max_characters=5000,
        )

        assert len(selected) == 1

        item = selected[0]

        assert item.chunk_id == child.id
        assert item.document_id == document.id
        assert item.text == child.text
        assert item.parent_text == parent.text

        assert (
            child.text
            in item.context_text
        )

        assert (
            parent.text
            in item.context_text
        )

    finally:
        if document is not None:
            cleanup_test_hierarchy(
                db,
                document.id,
            )

        db.close()


def test_select_context_respects_max_items():
    db = SessionLocal()

    document = None

    try:
        (
            document,
            parent,
            child,
        ) = create_test_hierarchy(db)

        result_one = FakeHybridResult(
            chunk_id=child.id,
            document_id=document.id,
            text=child.text,
            score=0.95,
            vector_score=0.94,
            text_score=0.90,
            rerank_score=0.95,
            page_number=1,
            section="Retrieval",
            subsection="Hybrid Search",
            chunk_level="child",
        )

        result_two = FakeHybridResult(
            chunk_id=parent.id,
            document_id=document.id,
            text=parent.text,
            score=0.80,
            vector_score=0.78,
            text_score=0.75,
            rerank_score=0.80,
            page_number=1,
            section="Retrieval",
            subsection="Hybrid Search",
            chunk_level="parent",
        )

        selected = select_context(
            db=db,
            results=[
                result_one,
                result_two,
            ],
            max_items=1,
            max_characters=5000,
        )

        assert len(selected) == 1

        assert (
            selected[0].chunk_id
            == child.id
        )

    finally:
        if document is not None:
            cleanup_test_hierarchy(
                db,
                document.id,
            )

        db.close()


def test_select_context_respects_character_budget():
    db = SessionLocal()

    document = None

    try:
        (
            document,
            parent,
            child,
        ) = create_test_hierarchy(db)

        result = FakeHybridResult(
            chunk_id=child.id,
            document_id=document.id,
            text=child.text,
            score=0.95,
            vector_score=0.94,
            text_score=0.90,
            rerank_score=0.95,
            page_number=1,
            section="Retrieval",
            subsection="Hybrid Search",
            chunk_level="child",
        )

        selected = select_context(
            db=db,
            results=[result],
            max_items=5,
            max_characters=10,
        )

        assert selected == []

    finally:
        if document is not None:
            cleanup_test_hierarchy(
                db,
                document.id,
            )

        db.close()


def test_select_context_deduplicates_chunks():
    db = SessionLocal()

    document = None

    try:
        (
            document,
            parent,
            child,
        ) = create_test_hierarchy(db)

        result = FakeHybridResult(
            chunk_id=child.id,
            document_id=document.id,
            text=child.text,
            score=0.95,
            vector_score=0.94,
            text_score=0.90,
            rerank_score=0.95,
            page_number=1,
            section="Retrieval",
            subsection="Hybrid Search",
            chunk_level="child",
        )

        selected = select_context(
            db=db,
            results=[
                result,
                result,
                result,
            ],
            max_items=5,
            max_characters=5000,
        )

        assert len(selected) == 1

        assert (
            selected[0].chunk_id
            == child.id
        )

    finally:
        if document is not None:
            cleanup_test_hierarchy(
                db,
                document.id,
            )

        db.close()
