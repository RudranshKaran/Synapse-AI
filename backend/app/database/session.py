"""Database engine and session management.

Provides SQLAlchemy engine, session factory, and FastAPI dependency
for database access throughout the application.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session.

    Yields a SQLAlchemy session, commits on success,
    rolls back on error, and always closes the session.

    Yields:
        SQLAlchemy Session instance.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
