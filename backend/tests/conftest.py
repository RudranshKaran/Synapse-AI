"""Test fixtures for Synapse AI.

Provides an in-memory SQLite database for testing,
FastAPI dependency overrides, and embedding mocks.
"""

from collections.abc import Generator
from unittest.mock import patch

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base
from app.database.session import get_db
from app.main import create_app

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override the get_db dependency with a test database session."""
    db = TestSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def mock_embeddings():
    """Mock Sentence Transformers to avoid model download during tests.

    Returns deterministic 384-dimensional unit vectors based on text hash.
    """
    with (
        patch("app.evaluation.embedding._load_model") as mock_load,
        patch("app.evaluation.embedding.SentenceTransformer") as mock_st,
    ):
        # Configure mock model
        mock_model = mock_load.return_value
        mock_st.return_value = mock_model

        def deterministic_encode(texts, normalize_embeddings=True):
            """Generate deterministic embeddings based on text content.

            Returns identical vectors for identical texts so that
            semantic similarity tests behave consistently.
            """
            if isinstance(texts, str):
                texts = [texts]
            vecs_list = []
            for t in texts:
                rng = np.random.RandomState(hash(t) % (2**31))
                v = rng.randn(384).astype(np.float32)
                vecs_list.append(v)
            vecs = np.array(vecs_list, dtype=np.float32)
            if normalize_embeddings:
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                vecs = vecs / norms
            return vecs if len(vecs) > 1 else vecs[0]

        mock_model.encode = deterministic_encode
        yield


@pytest.fixture(scope="function")
def app() -> FastAPI:
    """Create a fresh FastAPI instance for each test.

    Drops and recreates tables to ensure test isolation.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Provide a test client for API tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a raw database session for direct database assertions."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
