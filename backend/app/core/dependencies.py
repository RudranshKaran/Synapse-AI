"""Dependency injection for FastAPI routes.

Provides shared dependencies that can be injected into route handlers.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.consensus.engine import ConsensusEngine
from app.database.session import get_db
from app.evaluation.engine import EvaluationEngine
from app.repositories.debate_repository import DebateRepository
from app.services.debate_service import DebateService
from app.services.execution_service import ExecutionService
from app.services.metrics_service import MetricsService
from app.services.transcript_service import TranscriptService


def get_debate_repository(db: Session = Depends(get_db)) -> DebateRepository:
    """Provide a DebateRepository instance with an active database session.

    Args:
        db: SQLAlchemy database session.

    Returns:
        Configured DebateRepository.
    """
    return DebateRepository(db)


def get_debate_service(
    repository: DebateRepository = Depends(get_debate_repository),
) -> DebateService:
    """Provide a DebateService instance.

    Args:
        repository: DebateRepository for data access.

    Returns:
        Configured DebateService.
    """
    return DebateService(repository)


def get_execution_service(
    repository: DebateRepository = Depends(get_debate_repository),
) -> ExecutionService:
    """Provide an ExecutionService instance.

    Args:
        repository: DebateRepository for data access.

    Returns:
        Configured ExecutionService.
    """
    return ExecutionService(repository)


def get_transcript_service(
    repository: DebateRepository = Depends(get_debate_repository),
) -> TranscriptService:
    """Provide a TranscriptService instance."""
    return TranscriptService(repository)


def get_metrics_service(
    repository: DebateRepository = Depends(get_debate_repository),
) -> MetricsService:
    """Provide a MetricsService instance.

    Args:
        repository: DebateRepository for data access.

    Returns:
        Configured MetricsService.
    """
    return MetricsService(repository)
