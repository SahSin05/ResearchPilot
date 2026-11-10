from sqlalchemy.orm import Session

from app.database.models import DocumentChunkDB
from app.services.embeddings.base import EmbeddingProvider


def embed_pending_chunks(
    db: Session,
    provider: EmbeddingProvider,
    batch_size: int = 50,
    document_id: int | None = None,
) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    query = (
        db.query(DocumentChunkDB)
        .filter(DocumentChunkDB.embedding_status == "pending")
        .order_by(DocumentChunkDB.id.asc())
    )

    if document_id is not None:
        if document_id <= 0:
            raise ValueError("document_id must be greater than zero.")

        query = query.filter(
            DocumentChunkDB.document_id == document_id
        )

    chunks = query.all()

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
                    f"Invalid embedding dimension for chunk {chunk.id}: "
                    f"expected {provider.dimensions}, got {len(embedding)}."
                )

            chunk.embedding = embedding
            chunk.embedding_model = provider.model_name
            chunk.embedding_version = "v1"
            chunk.embedding_status = "completed"
            processed += 1

        db.commit()

    return processed