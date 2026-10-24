from sqlalchemy.orm import Session

from app.database.models import DocumentChunkDB
from app.services.embeddings.base import EmbeddingProvider


def embed_pending_chunks(
    db: Session,
    provider: EmbeddingProvider,
    batch_size: int = 50,
) -> int:
    """
    Generate and persist embeddings for pending document chunks.

    Returns the number of chunks successfully embedded.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    chunks = (
        db.query(DocumentChunkDB)
        .filter(
            DocumentChunkDB.embedding_status == "pending"
        )
        .order_by(DocumentChunkDB.id.asc())
        .all()
    )

    if not chunks:
        return 0

    processed = 0

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        texts = [chunk.text for chunk in batch]

        embeddings = provider.embed_documents(texts)

        if len(embeddings) != len(batch):
            raise RuntimeError(
                "Embedding count does not match chunk count."
            )

        for chunk, embedding in zip(batch, embeddings):
            if len(embedding) != provider.dimensions:
                raise RuntimeError(
                    f"Invalid embedding dimension for chunk "
                    f"{chunk.id}: expected {provider.dimensions}, "
                    f"got {len(embedding)}."
                )

            chunk.embedding = embedding
            chunk.embedding_model = provider.model_name
            chunk.embedding_version = "v1"
            chunk.embedding_status = "completed"

            processed += 1

        db.commit()

    return processed