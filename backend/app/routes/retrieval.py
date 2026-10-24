from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.retrieval import (
    CitationResponse,
    ContextItemResponse,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalResultResponse,
)

from app.services.embeddings import (
    create_embedding_provider,
)

from app.services.retrieval.hybrid_search import (
    hybrid_search,
)

from app.services.retrieval.context import (
    select_context,
)

from app.services.retrieval.citations import (
    build_citations,
)


router = APIRouter(
    prefix="/api/retrieval",
    tags=["retrieval"],
)


@router.post(
    "/search",
    response_model=RetrievalResponse,
)
def search_retrieval(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
):
    provider = create_embedding_provider()

    results = hybrid_search(
        db=db,
        query=request.query,
        embedding_provider=provider,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    context_items = select_context(
        db=db,
        results=results,
        max_items=5,
        max_characters=12000,
    )

    citations = build_citations(
        context_items
    )

    citation_by_chunk_id = {
        citation.chunk_id: citation
        for citation in citations
    }

    return RetrievalResponse(
        results=[
            RetrievalResultResponse(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                text=result.text,
                score=result.score,
                page_number=result.page_number,
                section=result.section,
                subsection=result.subsection,
                chunk_level=result.chunk_level,
            )
            for result in results
        ],
        context=[
            ContextItemResponse(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                text=item.text,
                parent_text=item.parent_text,
                context_text=item.context_text,
                score=item.score,
                rerank_score=item.rerank_score,
                page_number=item.page_number,
                section=item.section,
                subsection=item.subsection,
                chunk_level=item.chunk_level,
                citation=CitationResponse(
                    citation_id=citation_by_chunk_id[
                        item.chunk_id
                    ].citation_id,
                    chunk_id=citation_by_chunk_id[
                        item.chunk_id
                    ].chunk_id,
                    document_id=citation_by_chunk_id[
                        item.chunk_id
                    ].document_id,
                    label=citation_by_chunk_id[
                        item.chunk_id
                    ].label,
                    page_number=citation_by_chunk_id[
                        item.chunk_id
                    ].page_number,
                    section=citation_by_chunk_id[
                        item.chunk_id
                    ].section,
                    subsection=citation_by_chunk_id[
                        item.chunk_id
                    ].subsection,
                ),
            )
            for item in context_items
        ],
    )