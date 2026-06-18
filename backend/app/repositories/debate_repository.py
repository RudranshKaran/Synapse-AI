"""Debate repository — data access layer for debate entities."""

from collections.abc import Sequence
from datetime import datetime
import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.database.models.consensus_item import ConsensusItem
from app.database.models.consensus_report import ConsensusReport
from app.database.models.debate import Debate
from app.database.models.debate_round import DebateRound
from app.database.models.evaluation_metric import EvaluationMetric
from app.database.models.participant import Participant
from app.database.models.participant_metric import ParticipantMetric
from app.database.models.response import Response
from app.database.models.response_relationship import ResponseRelationship


class DebateRepository:
    """Repository for debate-related database operations.

    Encapsulates all SQLAlchemy queries for debates, participants,
    rounds, responses, and related entities.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Debate ──────────────────────────────────────────────

    def create_debate(self, question: str, total_rounds: int = 1) -> Debate:
        """Create a new debate record.

        Args:
            question: The debate question text.
            total_rounds: Number of debate rounds planned.

        Returns:
            The newly created Debate instance.
        """
        debate = Debate(question=question, total_rounds=total_rounds)
        self._db.add(debate)
        self._db.flush()
        return debate

    def get_debate_by_id(self, debate_id: uuid.UUID) -> Debate | None:
        """Retrieve a debate by its ID.

        Args:
            debate_id: The debate UUID.

        Returns:
            The Debate instance if found, otherwise None.
        """
        stmt = select(Debate).where(Debate.id == debate_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def update_debate_status(
        self, debate_id: uuid.UUID, status: str, completed_at: datetime | None = None
    ) -> None:
        """Update the status of a debate.

        Args:
            debate_id: The debate UUID.
            status: New status value.
            completed_at: Optional completion timestamp.
        """
        values: dict = {"status": status}
        if completed_at is not None:
            values["completed_at"] = completed_at
        stmt = update(Debate).where(Debate.id == debate_id).values(**values)
        self._db.execute(stmt)
        self._db.flush()

    # ── Listing ────────────────────────────────────────────

    def list_debates(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[Debate], int]:
        """List debates with pagination, filtering, and search.

        Args:
            page: Page number (1-based).
            page_size: Items per page.
            status_filter: Optional status to filter by.
            search: Optional text to search in question field.

        Returns:
            Tuple of (debates for current page, total count).
        """
        base_query = select(Debate)

        if status_filter:
            base_query = base_query.where(Debate.status == status_filter)
        if search:
            base_query = base_query.where(Debate.question.ilike(f"%{search}%"))

        # Total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total = self._db.execute(count_query).scalar_one()

        # Paginated results
        offset = (page - 1) * page_size
        stmt = (
            base_query
            .order_by(Debate.created_at.desc(), Debate.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        debates = self._db.execute(stmt).scalars().all()

        return debates, total

    def get_participant_counts(
        self, debate_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Get participant counts for multiple debates in one query.

        Args:
            debate_ids: List of debate UUIDs.

        Returns:
            Dict mapping debate_id → participant count.
        """
        if not debate_ids:
            return {}
        stmt = (
            select(
                Participant.debate_id,
                func.count(Participant.id).label("count"),
            )
            .where(Participant.debate_id.in_(debate_ids))
            .group_by(Participant.debate_id)
        )
        results = self._db.execute(stmt).all()
        return {row[0]: row[1] for row in results}

    def get_agreement_scores(
        self, debate_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, float]:
        """Get agreement scores for multiple debates in one query.

        Args:
            debate_ids: List of debate UUIDs.

        Returns:
            Dict mapping debate_id → agreement_score.
        """
        if not debate_ids:
            return {}
        stmt = (
            select(
                EvaluationMetric.debate_id,
                EvaluationMetric.metric_value,
            )
            .where(
                EvaluationMetric.debate_id.in_(debate_ids),
                EvaluationMetric.metric_name == "agreement_score",
            )
        )
        results = self._db.execute(stmt).all()
        return {row[0]: row[1] for row in results}

    # ── Participant ─────────────────────────────────────────

    def add_participant(
        self, debate_id: uuid.UUID, model_name: str, provider: str = "mock"
    ) -> Participant:
        """Add a participant to a debate.

        Args:
            debate_id: The debate UUID.
            model_name: Identifier for the model.
            provider: Provider name (e.g. "mock", "openai", "anthropic").

        Returns:
            The newly created Participant instance.
        """
        participant = Participant(
            debate_id=debate_id,
            model_name=model_name,
            provider=provider,
        )
        self._db.add(participant)
        self._db.flush()
        return participant

    def get_participants_for_debate(
        self, debate_id: uuid.UUID
    ) -> Sequence[Participant]:
        """Retrieve all participants for a debate.

        Args:
            debate_id: The debate UUID.

        Returns:
            List of Participant instances.
        """
        stmt = (
            select(Participant)
            .where(Participant.debate_id == debate_id)
            .order_by(Participant.created_at)
        )
        return self._db.execute(stmt).scalars().all()

    # ── Round ───────────────────────────────────────────────

    def create_round(
        self, debate_id: uuid.UUID, round_number: int, phase: str
    ) -> DebateRound:
        """Create a new debate round.

        Args:
            debate_id: The debate UUID.
            round_number: The round number (1-based).
            phase: Phase name (e.g. "opinion", "critique", "revision").

        Returns:
            The newly created DebateRound instance.
        """
        debate_round = DebateRound(
            debate_id=debate_id,
            round_number=round_number,
            phase=phase,
        )
        self._db.add(debate_round)
        self._db.flush()
        return debate_round

    # ── Response ────────────────────────────────────────────

    def create_response(
        self,
        debate_id: uuid.UUID,
        round_id: uuid.UUID,
        participant_id: uuid.UUID,
        response_type: str,
        content: str,
        confidence_score: float | None = None,
    ) -> Response:
        """Store a model-generated response.

        Args:
            debate_id: The debate UUID.
            round_id: The round UUID.
            participant_id: The participant UUID.
            response_type: Type of response (opinion, critique, etc.).
            content: The response text.
            confidence_score: Optional confidence score (0-100).

        Returns:
            The newly created Response instance.
        """
        response = Response(
            debate_id=debate_id,
            round_id=round_id,
            participant_id=participant_id,
            response_type=response_type,
            content=content,
            confidence_score=confidence_score,
        )
        self._db.add(response)
        self._db.flush()
        return response

    # ── Response Relationship ─────────────────────────────

    def create_response_relationship(
        self,
        source_response_id: uuid.UUID,
        target_response_id: uuid.UUID,
        relationship_type: str,
    ) -> ResponseRelationship:
        """Create a relationship between two responses.

        Used to link critiques to the opinions they target,
        and will support future relationship types (supports,
        influences, responds_to).

        Args:
            source_response_id: The response doing the relating (e.g. critique).
            target_response_id: The response being related to (e.g. opinion).
            relationship_type: Type of relationship (e.g. "critiques").

        Returns:
            The newly created ResponseRelationship instance.
        """
        relationship = ResponseRelationship(
            source_response_id=source_response_id,
            target_response_id=target_response_id,
            relationship_type=relationship_type,
        )
        self._db.add(relationship)
        self._db.flush()
        return relationship

    # ── Consensus ──────────────────────────────────────────

    def create_consensus_report(
        self,
        debate_id: uuid.UUID,
        consensus_score: float | None,
        summary: str | None,
    ) -> ConsensusReport:
        """Create a consensus report for a debate.

        Args:
            debate_id: The debate UUID.
            consensus_score: The computed consensus score (0-100).
            summary: A human-readable summary of the consensus.

        Returns:
            The newly created ConsensusReport instance.
        """
        report = ConsensusReport(
            debate_id=debate_id,
            consensus_score=consensus_score,
            summary=summary,
        )
        self._db.add(report)
        self._db.flush()
        return report

    def create_consensus_item(
        self,
        consensus_report_id: uuid.UUID,
        item_type: str,
        content: str,
    ) -> ConsensusItem:
        """Create a consensus item (agreement/disagreement) for a report.

        Args:
            consensus_report_id: The consensus report UUID.
            item_type: Type of item ("agreement", "disagreement", "uncertainty").
            content: The item text content.

        Returns:
            The newly created ConsensusItem instance.
        """
        item = ConsensusItem(
            consensus_report_id=consensus_report_id,
            item_type=item_type,
            content=content,
        )
        self._db.add(item)
        self._db.flush()
        return item

    # ── Evaluation Metrics ─────────────────────────────────

    def create_evaluation_metric(
        self,
        debate_id: uuid.UUID,
        metric_name: str,
        metric_value: float,
    ) -> EvaluationMetric:
        """Store a debate-level evaluation metric.

        Args:
            debate_id: The debate UUID.
            metric_name: Metric identifier (e.g. "agreement_score").
            metric_value: The computed metric value.

        Returns:
            The newly created EvaluationMetric instance.
        """
        metric = EvaluationMetric(
            debate_id=debate_id,
            metric_name=metric_name,
            metric_value=metric_value,
        )
        self._db.add(metric)
        self._db.flush()
        return metric

    def create_participant_metric(
        self,
        debate_id: uuid.UUID,
        participant_id: uuid.UUID,
        metric_name: str,
        metric_value: float,
    ) -> ParticipantMetric:
        """Store a participant-level evaluation metric.

        Args:
            debate_id: The debate UUID.
            participant_id: The participant UUID.
            metric_name: Metric identifier (e.g. "opinion_drift").
            metric_value: The computed metric value.

        Returns:
            The newly created ParticipantMetric instance.
        """
        metric = ParticipantMetric(
            debate_id=debate_id,
            participant_id=participant_id,
            metric_name=metric_name,
            metric_value=metric_value,
        )
        self._db.add(metric)
        self._db.flush()
        return metric

    def get_evaluation_metrics_for_debate(
        self, debate_id: uuid.UUID
    ) -> Sequence[EvaluationMetric]:
        """Retrieve all debate-level metrics for a debate.

        Args:
            debate_id: The debate UUID.

        Returns:
            List of EvaluationMetric instances.
        """
        stmt = (
            select(EvaluationMetric)
            .where(EvaluationMetric.debate_id == debate_id)
            .order_by(EvaluationMetric.created_at)
        )
        return self._db.execute(stmt).scalars().all()

    # ── Query helpers for transcript ───────────────────────

    def get_rounds_for_debate(
        self, debate_id: uuid.UUID
    ) -> Sequence[DebateRound]:
        """Retrieve all rounds for a debate, ordered by round number."""
        stmt = (
            select(DebateRound)
            .where(DebateRound.debate_id == debate_id)
            .order_by(DebateRound.round_number)
        )
        return self._db.execute(stmt).scalars().all()

    def get_responses_for_round(
        self, round_id: uuid.UUID
    ) -> Sequence[Response]:
        """Retrieve all responses for a given round."""
        stmt = (
            select(Response)
            .where(Response.round_id == round_id)
            .order_by(Response.created_at)
        )
        return self._db.execute(stmt).scalars().all()

    def get_relationships_for_response(
        self, response_id: uuid.UUID
    ) -> Sequence[ResponseRelationship]:
        """Retrieve all relationships where this response is the source."""
        stmt = select(ResponseRelationship).where(
            ResponseRelationship.source_response_id == response_id
        )
        return self._db.execute(stmt).scalars().all()

    def get_consensus_items_for_report(
        self, report_id: uuid.UUID
    ) -> Sequence[ConsensusItem]:
        """Retrieve all consensus items for a report."""
        stmt = select(ConsensusItem).where(
            ConsensusItem.consensus_report_id == report_id
        )
        return self._db.execute(stmt).scalars().all()

    def get_consensus_reports_for_debate(
        self, debate_id: uuid.UUID
    ) -> Sequence[ConsensusReport]:
        """Retrieve all consensus reports for a debate."""
        stmt = (
            select(ConsensusReport)
            .where(ConsensusReport.debate_id == debate_id)
            .order_by(ConsensusReport.created_at.desc())
        )
        return self._db.execute(stmt).scalars().all()

    def get_participant_metrics_for_debate(
        self, debate_id: uuid.UUID
    ) -> Sequence[ParticipantMetric]:
        """Retrieve all participant-level metrics for a debate.

        Args:
            debate_id: The debate UUID.

        Returns:
            List of ParticipantMetric instances.
        """
        stmt = (
            select(ParticipantMetric)
            .where(ParticipantMetric.debate_id == debate_id)
            .order_by(ParticipantMetric.metric_name)
        )
        return self._db.execute(stmt).scalars().all()
