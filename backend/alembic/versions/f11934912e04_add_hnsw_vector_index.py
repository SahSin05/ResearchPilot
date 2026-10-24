"""add hnsw vector index

Revision ID: <KEEP_GENERATED_REVISION_ID>
Revises: 6532b28dba22
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "<KEEP_GENERATED_REVISION_ID>"
down_revision = "6532b28dba22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WHERE embedding IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw
        """
    )