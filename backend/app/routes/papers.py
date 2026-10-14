from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.services.openalex import (
    search_works,
    search_authors,
    normalize_work,
    get_work,
)
from app.schemas.paper import Paper
from app.database.connection import SessionLocal
from app.database.models import PaperDB


router = APIRouter(
    prefix="/papers",
    tags=["papers"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/search")
async def search_papers(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    year: int | None = Query(None, ge=1900, le=2100),
    author: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    # -------------------------
    # Resolve author
    # -------------------------

    author_id = None

    if author is not None:
        author_results = await search_authors(author)

        if author_results.get("results"):
            author_id = author_results["results"][0].get("id")

    # -------------------------
    # Search OpenAlex
    # -------------------------

    results = await search_works(
        q,
        per_page,
        page,
        year,
        author_id,
    )

    # -------------------------
    # Normalize and save papers
    # -------------------------

    papers = []

    for work in results["results"]:
        normalized = normalize_work(work)

        existing_paper = (
            db.query(PaperDB)
            .filter(
                PaperDB.openalex_id == normalized["openalex_id"]
            )
            .first()
        )

        if not existing_paper:
            paper_db = PaperDB(
                openalex_id=normalized["openalex_id"],
                title=normalized["title"],
                publication_year=normalized["publication_year"],
                doi=normalized["doi"],
                authors=", ".join(normalized["authors"]),
                abstract=normalized["abstract"],
            )

            db.add(paper_db)

        paper = Paper(**normalized)
        papers.append(paper)

    db.commit()

    # -------------------------
    # Pagination information
    # -------------------------

    total = results.get("meta", {}).get("count", 0)

    total_pages = (
        (total + per_page - 1) // per_page
        if total > 0
        else 0
    )

    # -------------------------
    # Response
    # -------------------------

    return {
        "query": q,
        "page": page,
        "per_page": per_page,
        "count": len(papers),
        "total": total,
        "total_pages": total_pages,
        "papers": papers,
    }


@router.get("/{paper_id}", response_model=Paper)
async def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    # First try to find the paper in our database
    paper = (
        db.query(PaperDB)
        .filter(PaperDB.openalex_id == paper_id)
        .first()
    )

    if paper:
        authors = []

        if paper.authors:
            authors = [
                author.strip()
                for author in paper.authors.split(",")
            ]

        return Paper(
            id=paper.openalex_id,
            title=paper.title,
            publication_year=paper.publication_year,
            doi=paper.doi,
            authors=authors,
            abstract=paper.abstract,
            openalex_id=paper.openalex_id,
        )

    # If not found locally, fetch it from OpenAlex
    work = await get_work(paper_id)

    normalized = normalize_work(work)

    return Paper(**normalized)

@router.get("/")
def get_saved_papers(
    db: Session = Depends(get_db),
):
    papers = db.query(PaperDB).all()

    return [
        {
            "id": paper.id,
            "openalex_id": paper.openalex_id,
            "title": paper.title,
            "publication_year": paper.publication_year,
            "doi": paper.doi,
            "authors": paper.authors,
        }
        for paper in papers
    ]
