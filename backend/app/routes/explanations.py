from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import DocumentDB
from app.schemas.explanation import (
    ExplanationResponse,
    ExplanationSource,
)
from app.services.embeddings import create_embedding_provider
from app.services.generation.local_provider import LocalGenerationProvider
from app.services.explanation import ExplanationService
from app.services.retrieval.context import select_context
from app.services.retrieval.hybrid_search import hybrid_search


router = APIRouter(
    prefix="/api/explanations",
    tags=["explanations"],
)


@router.post(
    "/{document_id}/generate",
    response_model=ExplanationResponse,
)
def generate_explanation(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentDB)
        .filter(DocumentDB.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if document.processing_status != "completed":
        raise HTTPException(
            status_code=409,
            detail="Document processing is not complete.",
        )

    if not document.extracted_text or not document.extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Document contains no extracted text.",
        )

    try:
        embedding_provider = create_embedding_provider()
        results = hybrid_search(
            db=db,
            query=(
                "research problem objectives methodology methods "
                "dataset experimental setup results findings "
                "limitations assumptions conclusion key concepts"
            ),
            embedding_provider=embedding_provider,
            top_k=20,
            document_id=document_id,
        )
        context_items = select_context(
            db=db,
            results=results,
            max_items=10,
            max_characters=24000,
        )
        if not context_items:
            raise HTTPException(
                status_code=422,
                detail="No indexed evidence is available for this document.",
            )

        service = ExplanationService(
            provider=LocalGenerationProvider(),
        )
        explanation, citations = service.generate(
            filename=document.filename,
            context_items=context_items,
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate the paper explanation.",
        ) from exc

    sources = [
        ExplanationSource(
            citation_id=citation.citation_id,
            chunk_id=citation.chunk_id,
            document_id=citation.document_id,
            label=citation.label,
            page_number=citation.page_number,
            section=citation.section,
            subsection=citation.subsection,
        )
        for citation in citations
    ]

    return ExplanationResponse(
        document_id=document.id,
        filename=document.filename,
        explanation=explanation,
        sources=sources,
    )
