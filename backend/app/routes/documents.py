from pathlib import Path
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    DocumentDB,
    DocumentChunkDB,
)
from app.schemas.document import Document

from app.services.documents import (
    extract_pdf_text,
    extract_docx_text,
    extract_txt_text,
)

from app.services.ingestion import (
    prepare_document_chunks,
)


# --------------------------------
# Configuration
# --------------------------------

MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


# --------------------------------
# Router
# --------------------------------

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


# --------------------------------
# Upload document
# --------------------------------

@router.post(
    "/upload",
    response_model=Document,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # --------------------------------
    # Validate filename
    # --------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    # --------------------------------
    # Validate content type
    # --------------------------------

    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, DOCX, and TXT files "
                "are supported."
            ),
        )

    # --------------------------------
    # Read file
    # --------------------------------

    file_bytes = await file.read()

    file_size = len(file_bytes)

    # --------------------------------
    # Validate file size
    # --------------------------------

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 10MB.",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # --------------------------------
    # Generate storage path
    # --------------------------------

    file_extension = Path(
        file.filename
    ).suffix.lower()

    stored_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = UPLOAD_DIR / stored_filename

    # --------------------------------
    # Extract document
    # --------------------------------

    try:

        if file.content_type == "application/pdf":

            parsed_document = extract_pdf_text(
                file_bytes
            )

        elif file.content_type == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):

            parsed_document = extract_docx_text(
                file_bytes
            )

        elif file.content_type == "text/plain":

            parsed_document = extract_txt_text(
                file_bytes
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported document type.",
            )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to process the uploaded document."
            ),
        ) from exc

    # --------------------------------
    # Validate extracted text
    # --------------------------------

    if not parsed_document.text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was extracted "
                "from the document."
            ),
        )

    # --------------------------------
    # Save original file
    # --------------------------------

    try:

        file_path.write_bytes(
            file_bytes
        )

    except OSError as exc:

        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded file.",
        ) from exc

    # --------------------------------
    # Create document record
    # --------------------------------

    document = DocumentDB(
        filename=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        page_count=parsed_document.page_count,
        extracted_text=parsed_document.text,
        file_path=str(file_path),
        processing_status="processing",
        user_id="default-user",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:

        # --------------------------------
        # Prepare hierarchical chunks
        # --------------------------------

        chunks = prepare_document_chunks(
            parsed_document
        )

        # --------------------------------
        # Store chunks
        # --------------------------------

        chunk_records = []

        for chunk in chunks:

            chunk_record = DocumentChunkDB(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                chunk_level=chunk.chunk_level,
                parent_chunk_id=None,
                text=chunk.text,
                character_count=len(chunk.text),
                content_hash=chunk.content_hash,
                page_number=chunk.page_number,
                section=chunk.section,
                subsection=chunk.subsection,
                embedding_status="pending",
            )

            db.add(chunk_record)

            chunk_records.append(
                chunk_record
            )

        # --------------------------------
        # Resolve database IDs
        # --------------------------------

        db.flush()

        chunk_id_by_index = {
            chunk_record.chunk_index: chunk_record.id
            for chunk_record in chunk_records
        }

        # --------------------------------
        # Resolve parent relationships
        # --------------------------------

        for chunk, chunk_record in zip(
            chunks,
            chunk_records,
        ):

            if chunk.parent_chunk_index is None:
                continue

            parent_id = chunk_id_by_index.get(
                chunk.parent_chunk_index
            )

            if parent_id is None:

                raise RuntimeError(
                    "Unable to resolve parent database ID "
                    f"for chunk {chunk.chunk_index}: "
                    f"parent index "
                    f"{chunk.parent_chunk_index} "
                    "was not found."
                )

            chunk_record.parent_chunk_id = (
                parent_id
            )

        # --------------------------------
        # Mark processing complete
        # --------------------------------

        document.processing_status = (
            "completed"
        )

        db.commit()
        db.refresh(document)

    except Exception:

        # --------------------------------
        # Roll back database changes
        # --------------------------------

        db.rollback()

        # --------------------------------
        # Mark document as failed
        # --------------------------------

        try:

            document.processing_status = (
                "failed"
            )

            db.add(document)
            db.commit()

        except Exception:

            db.rollback()

        raise

    # --------------------------------
    # Response
    # --------------------------------

    return Document(
        id=str(document.id),
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        page_count=document.page_count,
        extracted_text=document.extracted_text,
    )


# --------------------------------
# Get all documents
# --------------------------------

@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
):
    documents = (
        db.query(DocumentDB)
        .order_by(
            DocumentDB.id.desc()
        )
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "page_count": document.page_count,
            "processing_status": (
                document.processing_status
            ),
            "user_id": document.user_id,
        }
        for document in documents
    ]


# --------------------------------
# Get single document
# --------------------------------

@router.get(
    "/{document_id}",
    response_model=Document,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentDB)
        .filter(
            DocumentDB.id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return Document(
        id=str(document.id),
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        page_count=document.page_count,
        extracted_text=document.extracted_text,
    )
