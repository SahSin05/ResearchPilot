from pydantic import BaseModel
from typing import Optional

class Paper(BaseModel):
    id: str
    title: str
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    authors: list[str] = []
    abstract: Optional[str] = None
    openalex_id: Optional[str] = None

