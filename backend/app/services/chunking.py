import hashlib
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    chunk_level: str
    parent_chunk_index: int | None
    page_number: int | None
    section: str | None
    subsection: str | None
    content_hash: str


def normalize_text(text: str) -> str:
    """
    Normalize extracted document text while preserving
    meaningful paragraph boundaries.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def calculate_content_hash(text: str) -> str:
    """
    Generate a deterministic SHA-256 hash for chunk content.
    """

    normalized = normalize_text(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split document text into meaningful paragraphs.
    """

    text = normalize_text(text)

    if not text:
        return []

    paragraphs = re.split(r"\n\s*\n", text)

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def _create_chunk(
    text: str,
    chunk_index: int,
    chunk_level: str,
    parent_chunk_index: int | None = None,
) -> Chunk:
    """
    Internal helper for creating a normalized Chunk.
    """

    text = normalize_text(text)

    return Chunk(
        text=text,
        chunk_index=chunk_index,
        chunk_level=chunk_level,
        parent_chunk_index=parent_chunk_index,
        page_number=None,
        section=None,
        subsection=None,
        content_hash=calculate_content_hash(text),
    )


def create_chunks(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
    parent_size: int = 3000,
) -> list[Chunk]:
    """
    Create hierarchical parent/child chunks.

    Parent chunks provide broader context.
    Child chunks are smaller retrieval units.

    The returned list contains both parent and child chunks.
    """

    text = normalize_text(text)

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    if parent_size <= chunk_size:
        raise ValueError(
            "parent_size must be greater than chunk_size"
        )

    paragraphs = split_into_paragraphs(text)

    if not paragraphs:
        return []

    chunks: list[Chunk] = []

    next_chunk_index = 0

    current_parent_text = ""
    parent_index: int | None = None

    def create_parent(parent_text: str) -> int:
        nonlocal next_chunk_index

        index = next_chunk_index

        chunks.append(
            _create_chunk(
                text=parent_text,
                chunk_index=index,
                chunk_level="parent",
            )
        )

        next_chunk_index += 1

        return index

    def create_child(
        child_text: str,
        parent_chunk_index: int,
    ) -> None:
        nonlocal next_chunk_index

        chunks.append(
            _create_chunk(
                text=child_text,
                chunk_index=next_chunk_index,
                chunk_level="child",
                parent_chunk_index=parent_chunk_index,
            )
        )

        next_chunk_index += 1

    for paragraph in paragraphs:

        candidate_parent = (
            paragraph
            if not current_parent_text
            else f"{current_parent_text}\n\n{paragraph}"
        )

        if (
            current_parent_text
            and len(candidate_parent) > parent_size
        ):
            parent_index = create_parent(
                current_parent_text
            )

            child_chunks = _split_text_into_children(
                current_parent_text,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            for child_text in child_chunks:
                create_child(
                    child_text,
                    parent_chunk_index=parent_index,
                )

            current_parent_text = paragraph

        else:
            current_parent_text = candidate_parent

    if current_parent_text:
        parent_index = create_parent(
            current_parent_text
        )

        child_chunks = _split_text_into_children(
            current_parent_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for child_text in child_chunks:
            create_child(
                child_text,
                parent_chunk_index=parent_index,
            )

    return chunks


def _split_text_into_children(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """
    Split a parent chunk into smaller child chunks.
    """

    paragraphs = split_into_paragraphs(text)

    children: list[str] = []

    current_text = ""

    for paragraph in paragraphs:

        candidate = (
            paragraph
            if not current_text
            else f"{current_text}\n\n{paragraph}"
        )

        if len(candidate) <= chunk_size:
            current_text = candidate
            continue

        if current_text:
            children.append(
                current_text.strip()
            )

        if len(paragraph) > chunk_size:
            start = 0

            while start < len(paragraph):
                end = start + chunk_size

                piece = paragraph[start:end].strip()

                if piece:
                    children.append(piece)

                if end >= len(paragraph):
                    break

                start = end - overlap

            current_text = ""

        else:
            current_text = paragraph

    if current_text:
        children.append(
            current_text.strip()
        )

    return children


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    """
    Backwards-compatible wrapper.

    Returns child chunk text only.
    """

    chunks = create_chunks(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return [
        chunk.text
        for chunk in chunks
        if chunk.chunk_level == "child"
    ]