from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSource,
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

from app.services.generation.local_provider import (
    LocalGenerationProvider,
)

from app.services.generation.service import (
    GenerationService,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    # 1. Create the embedding provider used by
    #    the existing Day 3 retrieval pipeline.
    embedding_provider = create_embedding_provider()

    # 2. Run the existing hybrid retrieval pipeline.
    results = hybrid_search(
        db=db,
        query=request.question,
        embedding_provider=embedding_provider,
        top_k=10,
        document_id=request.document_id,
    )

    # 3. Select and expand the best evidence.
    context_items = select_context(
        db=db,
        results=results,
        max_items=5,
        max_characters=12000,
    )

    if not context_items:
        return ChatResponse(
            answer=(
                "I could not find enough relevant evidence "
                "in the selected research paper to answer "
                "this question."
            ),
            sources=[],
        )

    # 4. Build citation metadata for the selected evidence.
    citations = build_citations(context_items)

    # 5. Prepare the evidence for the LLM.
    cited_context = []

    for citation, item in zip(
        citations,
        context_items,
    ):
        cited_context.append(
            f"{citation.label}\n"
            f"{item.context_text}"
        )

    # 6. Generate a grounded answer.
    provider = LocalGenerationProvider()

    generation_service = GenerationService(
        provider=provider,
    )

    answer = generation_service.generate_answer(
        question=request.question,
        context=cited_context,
    )

    # 7. Return the answer together with its sources.
    sources = [
        ChatSource(
            citation_id=str(citation.citation_id),
            chunk_id=citation.chunk_id,
            document_id=citation.document_id,
            label=citation.label,
            page_number=citation.page_number,
            section=citation.section,
            subsection=citation.subsection,
        )
        for citation in citations
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
    )