"""add full text search index

Revision ID: bcc48c54ae0d
Revises: <KEEP_GENERATED_REVISION_ID>
Create Date: 2026-10-24 04:31:09.549202

"""
from alembic import op


from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcc48c54ae0d'
down_revision: Union[str, Sequence[str], None] = '<KEEP_GENERATED_REVISION_ID>'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_text_fts
        ON document_chunks
        USING gin (
            to_tsvector('english', text)
        )
        """
    )

def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_document_chunks_text_fts
        """
    )
