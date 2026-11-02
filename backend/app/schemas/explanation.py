from pydantic import BaseModel, Field


class ExplanationSource(BaseModel):
    citation_id: int
    chunk_id: int
    document_id: int
    label: str
    page_number: int | None = None
    section: str | None = None
    subsection: str | None = None


class ExplanationResponse(BaseModel):
    document_id: int
    filename: str
    explanation: str
    sources: list[ExplanationSource]
