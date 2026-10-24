from app.services.chunking import (
    calculate_content_hash,
    chunk_text,
    create_chunks,
    normalize_text,
)


TEXT = """
ResearchPilot is an AI research assistant.

It helps researchers discover papers,
upload documents, understand research,
and ask questions grounded in their sources.

The system will eventually use retrieval
augmented generation to retrieve relevant
sections of documents before generating answers.
"""


def test_normalize_text():
    text = "hello   world\r\n\r\n\r\nnext paragraph"

    normalized = normalize_text(text)

    assert normalized == (
        "hello world\n\nnext paragraph"
    )


def test_content_hash_is_deterministic():
    text = "ResearchPilot AI"

    first = calculate_content_hash(text)
    second = calculate_content_hash(text)

    assert first == second
    assert len(first) == 64


def test_create_chunks_generates_parent_and_child_chunks():
    chunks = create_chunks(
        TEXT,
        chunk_size=120,
        overlap=20,
        parent_size=250,
    )

    assert chunks

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

        assert child.text
        assert parent.text


def test_parent_chunks_are_larger_than_child_chunks():
    chunks = create_chunks(
        TEXT,
        chunk_size=120,
        overlap=20,
        parent_size=250,
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
        parent = next(
            parent
            for parent in parents
            if parent.chunk_index
            == child.parent_chunk_index
        )

        assert len(parent.text) >= len(child.text)


def test_chunk_text_returns_only_child_chunks():
    chunks = chunk_text(
        TEXT,
        chunk_size=120,
        overlap=20,
    )

    assert chunks

    for chunk in chunks:
        assert isinstance(chunk, str)
        assert chunk.strip()


def test_empty_text_returns_no_chunks():
    assert create_chunks("") == []
    assert chunk_text("") == []


def test_invalid_chunk_configuration():
    try:
        create_chunks(
            TEXT,
            chunk_size=100,
            overlap=100,
        )
        assert False
    except ValueError:
        pass

    try:
        create_chunks(
            TEXT,
            chunk_size=100,
            overlap=20,
            parent_size=100,
        )
        assert False
    except ValueError:
        pass