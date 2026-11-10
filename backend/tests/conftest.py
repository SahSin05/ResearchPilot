import os
import sys
import tempfile
from pathlib import Path

# Ensure backend directory is importable.
BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# Create a fresh SQLite database for this test session.
fd, TEST_DB_PATH = tempfile.mkstemp(
    prefix="researchpilot_test_",
    suffix=".db",
)
os.close(fd)

# Set the database URL before importing application modules.
os.environ["DATABASE_URL"] = (
    f"sqlite:///{TEST_DB_PATH.replace(os.sep, '/')}"
)

# Import database configuration after setting DATABASE_URL.
from app.database.connection import (
    Base,
    engine,
    SessionLocal,
    get_db,
)
from app.database import models

# Create the test database tables.
Base.metadata.create_all(bind=engine)


# Make FastAPI use the test database for requests.
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.main import app

app.dependency_overrides[get_db] = override_get_db


def pytest_sessionfinish(session, exitstatus):
    """Close and remove the temporary test database."""

    app.dependency_overrides.clear()
    engine.dispose()
    Path(TEST_DB_PATH).unlink(missing_ok=True)