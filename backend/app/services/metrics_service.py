"""Metrics service — retrieves computed evaluation metrics for debates."""

import uuid

from fastapi import HTTPException, status

from app.repositories.debate_repository import DebateRepository
from app.schemas.metrics import MetricsResponse


class MetricsService:
    """Service for retrieving debate evaluation metrics."""

    def __init__(self, repository: DebateRepository) -> None:
        self._repository = repository

    def get_metrics(self, debate_id: str) -> MetricsResponse:
        """Retrieve all computed metrics for a debate.

        Args:
            debate_id: The debate UUID as a string.

        Returns:
            MetricsResponse with agreement_score, opinion_drifts,
            and confidence_shifts.

        Raises:
            HTTPException: If debate not found or UUID invalid.
        """
        try:
            debate_uuid = uuid.UUID(debate_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid debate ID format: {debate_id}",
            )

        debate = self._repository.get_debate_by_id(debate_uuid)
        if debate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate not found: {debate_id}",
            )

        # Get debate-level metrics
        debate_metrics = self._repository.get_evaluation_metrics_for_debate(debate_uuid)
        agreement_score: float | None = None
        for m in debate_metrics:
            if m.metric_name == "agreement_score":
                agreement_score = m.metric_value

        # Get participant-level metrics
        participant_metrics = self._repository.get_participant_metrics_for_debate(
            debate_uuid
        )
        participants = self._repository.get_participants_for_debate(debate_uuid)
        pid_to_model = {str(p.id): p.model_name for p in participants}

        opinion_drifts: dict[str, float] = {}
        confidence_shifts: dict[str, float] = {}

        for pm in participant_metrics:
            pid_str = str(pm.participant_id)
            model_key = pid_to_model.get(pid_str, pid_str)
            if pm.metric_name == "opinion_drift":
                opinion_drifts[model_key] = pm.metric_value
            elif pm.metric_name == "confidence_shift":
                confidence_shifts[model_key] = pm.metric_value

        return MetricsResponse(
            debate_id=debate_id,
            agreement_score=agreement_score,
            opinion_drifts=opinion_drifts,
            confidence_shifts=confidence_shifts,
        )
