from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.service import create_embedding_provider


def test_embedding_provider_factory():
    provider = create_embedding_provider()

    assert isinstance(provider, EmbeddingProvider)
    assert provider.model_name == "text-embedding-3-small"
    assert provider.dimensions == 1536