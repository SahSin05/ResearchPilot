from dataclasses import dataclass
import io

import fitz
from docx import Document as DocxDocument


@dataclass
class ParsedPage:
    page_number: int
    text: str


@dataclass
class ParsedDocument:
    text: str
    page_count: int
    pages: list[ParsedPage]


def _clean_text(text: str) -> str:
    """
    Normalize extracted text while preserving paragraph boundaries.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def extract_pdf_text(file_bytes: bytes) -> ParsedDocument:
    """
    Extract PDF text while preserving page boundaries.
    """

    pdf = fitz.open(
        stream=file_bytes,
        filetype="pdf",
    )

    pages: list[ParsedPage] = []

    for index, page in enumerate(pdf):
        text = page.get_text("text")
        text = _clean_text(text)

        pages.append(
            ParsedPage(
                page_number=index + 1,
                text=text,
            )
        )

    page_count = len(pages)

    full_text = "\n\n".join(
        page.text
        for page in pages
        if page.text
    )

    pdf.close()

    return ParsedDocument(
        text=full_text,
        page_count=page_count,
        pages=pages,
    )


def extract_docx_text(file_bytes: bytes) -> ParsedDocument:
    """
    Extract DOCX paragraphs.

    DOCX does not have reliable page boundaries at the
    document XML level, so paragraphs are preserved as
    structured text without inventing page numbers.
    """

    document = DocxDocument(
        io.BytesIO(file_bytes)
    )

    paragraphs = []

    for paragraph in document.paragraphs:
        text = _clean_text(paragraph.text)

        if text:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)

    return ParsedDocument(
        text=full_text,
        page_count=None,
        pages=[
            ParsedPage(
                page_number=1,
                text=full_text,
            )
        ],
    )


def extract_txt_text(file_bytes: bytes) -> ParsedDocument:
    """
    Extract plain-text documents.
    """

    text = file_bytes.decode(
        "utf-8",
        errors="replace",
    )

    text = _clean_text(text)

    return ParsedDocument(
        text=text,
        page_count=1,
        pages=[
            ParsedPage(
                page_number=1,
                text=text,
            )
        ],
    )
