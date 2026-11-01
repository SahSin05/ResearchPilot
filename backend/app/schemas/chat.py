from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    document_id: int
    question: str = Field(min_length=1, max_length=2000)


class ChatSource(BaseModel):
    citation_id: str
    chunk_id: int
    document_id: int
    label: str
    page_number: int | None = None
    section: str | None = None
    subsection: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]