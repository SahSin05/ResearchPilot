from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import DocumentDB

from app.services.embeddings import (
    create_embedding_provider,
)

from app.services.generation.explanation import (
    ExplanationService,
)

from app.services.generation.provider import (
    create_generation_provider,
)

from app.services.generation.paper_evidence import (
    collect_paper_evidence,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["explanation"],
)


@router.get(
    "/{document_id}/explanation",
)
def explain_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    # --------------------------------
    # Validate document
    # --------------------------------

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

    # --------------------------------
    # Validate processing status
    # --------------------------------

    if document.processing_status != "completed":
        raise HTTPException(
            status_code=409,
            detail=(
                "The document has not finished processing."
            ),
        )

    # --------------------------------
    # Create embedding provider
    # --------------------------------

    embedding_provider = create_embedding_provider()

    # --------------------------------
    # Collect paper evidence
    # --------------------------------

    try:
        cited_context = collect_paper_evidence(
            db=db,
            document_id=document_id,
            embedding_provider=embedding_provider,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if not cited_context:
        raise HTTPException(
            status_code=404,
            detail=(
                "No relevant research evidence was found "
                "for this document."
            ),
        )

    # --------------------------------
    # Generate explanation
    # --------------------------------

    provider = create_generation_provider()

    explanation_service = ExplanationService(
        provider=provider,
    )

    try:
        explanation = explanation_service.explain(
            context=cited_context,
        )

    except (RuntimeError, ValueError) as exc:
        print("EXPLANATION GENERATION ERROR:")
        print(repr(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
       

    # --------------------------------
    # Return structured explanation
    # --------------------------------

    return explanation