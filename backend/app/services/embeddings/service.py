from functools import lru_cache

from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.local_provider import LocalEmbeddingProvider


@lru_cache(maxsize=1)
def create_embedding_provider() -> EmbeddingProvider:
    """
    Create and cache a single embedding provider instance.

    The Sentence Transformer model is expensive to load, so we keep
    one provider alive for the lifetime of the backend process.
    """
    return LocalEmbeddingProvider()