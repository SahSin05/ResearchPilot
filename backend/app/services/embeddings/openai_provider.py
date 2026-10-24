import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.services.embeddings.base import EmbeddingProvider


PROJECT_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(PROJECT_ROOT / ".env")


class OpenAIEmbeddingProvider(EmbeddingProvider):

    def __init__(
        self,
        model: str | None = None,
        dimensions: int | None = None,
    ):
        self._model = model or os.getenv(
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )

        self._dimensions = dimensions or int(
            os.getenv("EMBEDDING_DIMENSIONS", "1536")
        )

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self._model,
            input=texts,
            dimensions=self._dimensions,
        )

        embeddings = [
            item.embedding
            for item in response.data
        ]

        if len(embeddings) != len(texts):
            raise RuntimeError(
                "Embedding provider returned an unexpected "
                "number of embeddings."
            )

        for embedding in embeddings:
            if len(embedding) != self._dimensions:
                raise RuntimeError(
                    f"Expected embedding dimension "
                    f"{self._dimensions}, got {len(embedding)}."
                )

        return embeddings

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        if not text.strip():
            raise ValueError(
                "Query text cannot be empty."
            )

        response = self.client.embeddings.create(
            model=self._model,
            input=text,
            dimensions=self._dimensions,
        )

        embedding = response.data[0].embedding

        if len(embedding) != self._dimensions:
            raise RuntimeError(
                f"Expected embedding dimension "
                f"{self._dimensions}, got {len(embedding)}."
            )

        return embedding