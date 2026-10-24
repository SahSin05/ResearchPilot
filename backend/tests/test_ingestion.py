from types import SimpleNamespace

from app.services.ingestion import prepare_document_chunks


def test_prepare_document_chunks_preserves_parent_relationships():

    document = SimpleNamespace(
        pages=[
            SimpleNamespace(
                page_number=1,
                text="""
                ResearchPilot is an AI research assistant.

                It helps researchers discover papers,
                upload documents, understand research,
                and ask questions grounded in sources.

                Retrieval augmented generation retrieves
                relevant sections before generating answers.
                """,
            )
        ]
    )

    chunks = prepare_document_chunks(
        document,
        chunk_size=80,
        overlap=10,
        parent_size=180,
    )

    parents = [
        chunk
        for chunk in chunks
        if chunk.chunk_level == "parent"
    ]

    children = [
        chunk
        for chunk in chunks
        if chunk.chunk_level == "child"
    ]

    assert parents
    assert children

    for child in children:
        assert child.parent_chunk_index is not None

        parent = next(
            parent
            for parent in parents
            if parent.chunk_index
            == child.parent_chunk_index
        )

        assert parent.page_number == child.page_number


def test_prepare_document_chunks_uses_global_indexes():

    document = SimpleNamespace(
        pages=[
            SimpleNamespace(
                page_number=1,
                text="""
                First page content.

                More first page content.

                Additional first page information.
                """,
            ),
            SimpleNamespace(
                page_number=2,
                text="""
                Second page content.

                More second page content.

                Additional second page information.
                """,
            ),
        ]
    )

    chunks = prepare_document_chunks(
        document,
        chunk_size=80,
        overlap=10,
        parent_size=180,
    )

    indexes = [
        chunk.chunk_index
        for chunk in chunks
    ]

    assert indexes == list(
        range(len(chunks))
    )

    for chunk in chunks:
        if chunk.parent_chunk_index is not None:
            assert (
                chunk.parent_chunk_index
                < chunk.chunk_index
            )