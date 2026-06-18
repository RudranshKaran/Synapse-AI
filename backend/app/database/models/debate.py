"""Debate model — top-level entity for debate sessions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class Debate(Base):
    __tablename__ = "debates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="created", index=True
    )
    total_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    participants = relationship(
        "Participant", back_populates="debate", cascade="all, delete-orphan"
    )
    rounds = relationship(
        "DebateRound", back_populates="debate", cascade="all, delete-orphan"
    )
    consensus_reports = relationship(
        "ConsensusReport", back_populates="debate", cascade="all, delete-orphan"
    )
    evaluation_metrics = relationship(
        "EvaluationMetric", back_populates="debate", cascade="all, delete-orphan"
    )
