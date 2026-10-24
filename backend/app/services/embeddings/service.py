import os

from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.openai_provider import OpenAIEmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    provider = os.getenv(
        "EMBEDDING_PROVIDER",
        "openai",
    ).lower()

    if provider == "openai":
        return OpenAIEmbeddingProvider()

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )