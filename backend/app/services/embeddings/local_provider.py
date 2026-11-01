from sentence_transformers import SentenceTransformer

from app.services.embeddings.base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local Sentence Transformer embedding provider."""

    def __init__(
        self,
        model: str = "sentence-transformers/all-mpnet-base-v2",
    ) -> None:
        self._model = model
        self._encoder = SentenceTransformer(model)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._encoder.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self._encoder.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        embedding = self._encoder.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.tolist()