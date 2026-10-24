from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    document_id: int | None = Field(default=None, ge=1)


class RetrievalResultResponse(BaseModel):
    chunk_id: int
    document_id: int
    text: str
    score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str


class ContextItemResponse(BaseModel):
    chunk_id: int
    document_id: int
    text: str
    parent_text: str | None
    context_text: str
    score: float
    rerank_score: float
    page_number: int | None
    section: str | None
    subsection: str | None
    chunk_level: str
    citation: CitationResponse


class RetrievalResponse(BaseModel):
    results: list[RetrievalResultResponse]
    context: list[ContextItemResponse]

class CitationResponse(BaseModel):
    citation_id: int
    chunk_id: int
    document_id: int
    label: str
    page_number: int | None
    section: str | None
    subsection: str | None    