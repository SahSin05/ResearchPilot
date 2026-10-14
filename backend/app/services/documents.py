import fitz
from docx import Document

def extract_pdf_text(file_bytes: bytes)->tuple[str,int]:
    pdf=fitz.open(
        stream=file_bytes,
        filetype="pdf",
    )

    page_count=len(pdf)
    text=""

    for page in pdf:
        text+=page.get_text()
    pdf.close()
    return text, page_count

def extract_docx_text(file_bytes: bytes) -> tuple[str, int]:
    import io

    document = Document(io.BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    text = "\n".join(paragraphs)

    return text, len(document.paragraphs)


def extract_txt_text(file_bytes: bytes) -> tuple[str, int]:
    text = file_bytes.decode("utf-8")

    return text, 1 
