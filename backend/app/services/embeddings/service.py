import os

from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.services.embeddings.local_provider import LocalEmbeddingProvider

def create_embedding_provider() -> EmbeddingProvider:
    provider = os.getenv(
        "EMBEDDING_PROVIDER",
        "local",
    ).lower()

    if provider == "local":
        return LocalEmbeddingProvider()

    if provider =="openai":
        return OpenAIEmbeddingProvider()

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )