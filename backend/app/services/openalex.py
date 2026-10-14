import os

import httpx

from dotenv import load_dotenv
import asyncio
from fastapi import HTTPException

load_dotenv()


OPENALEX_BASE_URL = "https://api.openalex.org"
OPENALEX_API_KEY=os.getenv("OPENALEX_API_KEY")

async def search_works(
    query: str,
    per_page: int = 10,
    page: int = 1,
    year: int | None = None,
    author_id: str | None = None,
):
    url = f"{OPENALEX_BASE_URL}/works"

    params = {
        "search": query,
        "per-page": per_page,
        "page": page,
    }

    if OPENALEX_API_KEY:
        params["api_key"]=OPENALEX_API_KEY

    filters = []

    if year is not None:
        filters.append(f"publication_year:{year}")

    if author_id is not None:
        filters.append(f"author.id:{author_id}")

    if filters:
        params["filter"] = ",".join(filters)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            params=params,
            headers={
                "User-Agent": "ResearchPilot/1.0",
            },
        )

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="OpenAlex rate limit reached. Please wait a moment and try again.",
        )

    response.raise_for_status()

    return response.json()


async def search_authors(name: str):
    url = f"{OPENALEX_BASE_URL}/authors"

    params = {
        "search": name,
        "per-page": 5,
    }

    if OPENALEX_API_KEY:
        params["api_key"]=OPENALEX_API_KEY

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            params=params,
        )

    response.raise_for_status()

    return response.json()


def normalize_work(work: dict) -> dict:
    """Convert an OpenAlex work into the format expected by ResearchPilot.
    """

    authors = []

    for authorship in work.get("authorships", []):
        author = authorship.get("author")

        if author and author.get("display_name"):
            authors.append(author["display_name"])

    abstract = None

    inverted_index = work.get("abstract_inverted_index")

    if inverted_index:
        words = []

        for word, positions in inverted_index.items():
            for position in positions:
                words.append((position, word))

        words.sort(key=lambda item: item[0])

        abstract = " ".join(
            word for _, word in words
        )

    return {
        "id": work.get("id"),
        "title": work.get("title") or "Untitled",
        "publication_year": work.get("publication_year"),
        "doi": work.get("doi"),
        "authors": authors,
        "abstract": abstract,
        "openalex_id": work.get("id"),
    }


async def get_work(work_id: str):
    url = f"{OPENALEX_BASE_URL}/works/{work_id}"

    params = {}

    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            params=params,
        )

    response.raise_for_status()

    return response.json()

