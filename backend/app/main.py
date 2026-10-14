import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.papers import router as paper_router
from app.routes.documents import router as document_router

from app.database.connection import engine, Base
from app.database.models import DocumentDB, DocumentChunkDB

from pydantic import BaseModel

def parse_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

app = FastAPI(
    title="ResearchPilot AI API",
    description="API for research discovery, document intelligence, RAG, and LLM evaluation.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(paper_router)
app.include_router(document_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    service: str

@app.get("/", tags=["meta"])
def root():
    return {"message": "ResearchPilot AI API", "docs": "/docs", "health": "/health"}

@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    return HealthResponse(status="ok", service="researchpilot-api")

