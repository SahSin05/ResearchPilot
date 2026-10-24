from io import BytesIO

from fastapi.testclient import TestClient

from app.database.connection import SessionLocal
from app.database.models import (
    DocumentChunkDB,
    DocumentDB,
)
from app.main import app


client = TestClient(app)


def test_document_upload_persists_parent_child_relationships():
    """
    Verify that uploading a document:

    1. Creates a document record.
    2. Creates hierarchical parent/child chunks.
    3. Persists parent_chunk_id for child chunks.
    4. Keeps parent chunks without a parent.
    """

    document_text = """
    ResearchPilot is an AI research assistant.

    It helps researchers discover papers, upload documents,
    understand research, and ask questions grounded in sources.

    Retrieval augmented generation retrieves relevant sections
    before generating answers.

    The retrieval system combines vector search and PostgreSQL
    full-text search to improve document retrieval quality.

    Reciprocal rank fusion combines the results from both
    retrieval strategies before reranking.
    """

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test_research.txt",
                BytesIO(
                    document_text.encode("utf-8")
                ),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "id" in response_data
    assert response_data["filename"] == "test_research.txt"

    document_id = int(
        response_data["id"]
    )

    db = SessionLocal()

    try:

        # --------------------------------
        # Verify document exists
        # --------------------------------

        document = (
            db.query(DocumentDB)
            .filter(
                DocumentDB.id == document_id
            )
            .first()
        )

        assert document is not None

        assert (
            document.processing_status
            == "completed"
        )

        # --------------------------------
        # Load persisted chunks
        # --------------------------------

        chunks = (
            db.query(DocumentChunkDB)
            .filter(
                DocumentChunkDB.document_id
                == document_id
            )
            .order_by(
                DocumentChunkDB.chunk_index.asc()
            )
            .all()
        )

        assert chunks

        # --------------------------------
        # Separate parents and children
        # --------------------------------

        parents = [
            chunk
            for chunk in chunks
            if chunk.chunk_level == "parent"
        ]

        children = [
            chunk
            for chunk in chunks
            if chunk.chunk_level == "child"
        ]

        assert parents
        assert children

        # --------------------------------
        # Verify parent chunks
        # --------------------------------

        for parent in parents:

            assert (
                parent.parent_chunk_id
                is None
            )

        # --------------------------------
        # Verify child relationships
        # --------------------------------

        parent_ids = {
            parent.id
            for parent in parents
        }

        for child in children:

            assert (
                child.parent_chunk_id
                is not None
            )

            assert (
                child.parent_chunk_id
                in parent_ids
            )

            parent = (
                db.query(DocumentChunkDB)
                .filter(
                    DocumentChunkDB.id
                    == child.parent_chunk_id
                )
                .first()
            )

            assert parent is not None

            assert (
                parent.document_id
                == child.document_id
            )

            assert (
                parent.chunk_level
                == "parent"
            )

        # --------------------------------
        # Verify chunk indexes
        # --------------------------------

        chunk_indexes = [
            chunk.chunk_index
            for chunk in chunks
        ]

        assert chunk_indexes == list(
            range(len(chunks))
        )

    finally:

        # --------------------------------
        # Clean up test data
        # --------------------------------

        db.close()

        cleanup_db = SessionLocal()

        try:

            chunks_to_delete = (
                cleanup_db.query(
                    DocumentChunkDB
                )
                .filter(
                    DocumentChunkDB.document_id
                    == document_id
                )
                .all()
            )

            for chunk in chunks_to_delete:
                cleanup_db.delete(chunk)

            document_to_delete = (
                cleanup_db.query(
                    DocumentDB
                )
                .filter(
                    DocumentDB.id
                    == document_id
                )
                .first()
            )

            if document_to_delete:
                cleanup_db.delete(
                    document_to_delete
                )

            cleanup_db.commit()

        finally:

            cleanup_db.close()
