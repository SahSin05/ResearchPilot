from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
import uuid

from sqlalchemy.orm import Session


from app.schemas.document import Document
from app.database.connection import SessionLocal
from app.database.models import DocumentDB, DocumentChunkDB
from app.services.chunking import chunk_text


from app.services.documents import (
    extract_pdf_text,
    extract_docx_text,
    extract_txt_text,
)

MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)
    file_extension = Path(file.filename).suffix
    stored_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / stored_filename

    file_path.write_bytes(file_bytes)

    if file_size>MAX_FILE_SIZE:
        raise HTTPException(

            status_code=400,
            detail="File size must not exceed 10MB."
        )

    if file.content_type == "application/pdf":
        text, page_count = extract_pdf_text(file_bytes)

    elif file.content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        text, page_count = extract_docx_text(file_bytes)

    elif file.content_type == "text/plain":
        text, page_count = extract_txt_text(file_bytes)

    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are supported",
        )
    

    document = DocumentDB(
        filename=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        page_count=page_count,
        extracted_text=text,
        file_path=str(file_path),
        processing_status="completed",
        user_id="default-user",
    )


    db.add(document)
    db.commit()
    db.refresh(document)

    chunks=chunk_text(text)

    for index,chunk in enumerate(chunks):
        chunk_record=DocumentChunkDB(
            document_id=document.id,
            chunk_index=index,
            text=chunk,
            character_count=len(chunk),
        )
        db.add(chunk_record)
    db.commit()    


    return Document(
        id=str(document.id),
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        page_count=document.page_count,
        extracted_text=document.extracted_text,
    )

@router.get("/")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(DocumentDB).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "page_count": document.page_count,
        }
        for document in documents
    ]


@router.get("/{document_id}",response_model=Document)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document=(
        db.query(DocumentDB)
        .filter(DocumentDB.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document Not Found"
        )

    return Document(
        id=str(document.id),
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        extracted_text=document.extracted_text,
    )
@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
):
    documents = (
        db.query(DocumentDB)
        .order_by(DocumentDB.id.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "page_count": document.page_count,
            "extracted_text": document.extracted_text,
            "file_path": document.file_path,
            "processing_status": document.processing_status,
            "user_id": document.user_id,
        }
        for document in documents
    ]