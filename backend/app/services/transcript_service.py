"""Transcript service — assembles complete debate history for the transcript endpoint."""

import uuid

from fastapi import HTTPException, status

from app.repositories.debate_repository import DebateRepository
from app.schemas.transcript import (
    Transcript,
    TranscriptConsensus,
    TranscriptEntry,
    TranscriptMetricsInfo,
    TranscriptParticipant,
    TranscriptRound,
)


class TranscriptService:
    """Service for assembling complete debate transcripts."""

    def __init__(self, repository: DebateRepository) -> None:
        self._repository = repository

    def get_transcript(self, debate_id: str) -> Transcript:
        """Retrieve the complete transcript for a debate.

        Assembles all debate artifacts — participants, rounds,
        responses, relationships, consensus, and metrics — into
        a single response suitable for frontend consumption.

        Args:
            debate_id: The debate UUID as a string.

        Returns:
            Transcript with all debate data.

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

        # Participants
        participants = self._repository.get_participants_for_debate(debate_uuid)
        participant_map = {str(p.id): p for p in participants}
        transcript_participants = [
            TranscriptParticipant(
                participant_id=str(p.id),
                model_name=p.model_name,
                provider=p.provider,
            )
            for p in participants
        ]

        # Rounds and responses
        rounds = self._repository.get_rounds_for_debate(debate_uuid)
        transcript_rounds: list[TranscriptRound] = []

        for debate_round in rounds:
            responses = self._repository.get_responses_for_round(debate_round.id)
            transcript_entries: list[TranscriptEntry] = []

            for resp in responses:
                participant = participant_map.get(str(resp.participant_id))
                relationships = self._repository.get_relationships_for_response(resp.id)
                transcript_entries.append(
                    TranscriptEntry(
                        response_id=str(resp.id),
                        participant_id=str(resp.participant_id),
                        model_name=participant.model_name if participant else "unknown",
                        response_type=resp.response_type,
                        content=resp.content,
                        confidence_score=resp.confidence_score,
                        created_at=resp.created_at,
                        relationships=[
                            {
                                "relationship_id": str(r.id),
                                "target_response_id": str(r.target_response_id),
                                "relationship_type": r.relationship_type,
                            }
                            for r in relationships
                        ],
                    )
                )

            transcript_rounds.append(
                TranscriptRound(
                    round_id=str(debate_round.id),
                    round_number=debate_round.round_number,
                    phase=debate_round.phase,
                    created_at=debate_round.created_at,
                    responses=transcript_entries,
                )
            )

        # Consensus
        consensus_reports = self._repository.get_consensus_reports_for_debate(debate_uuid)
        transcript_consensus: TranscriptConsensus | None = None
        if consensus_reports:
            report = consensus_reports[0]
            items = self._repository.get_consensus_items_for_report(report.id)
            transcript_consensus = TranscriptConsensus(
                consensus_score=report.consensus_score,
                agreements=[i.content for i in items if i.item_type == "agreement"],
                disagreements=[i.content for i in items if i.item_type == "disagreement"],
                summary=report.summary,
            )

        # Metrics
        debate_metrics = self._repository.get_evaluation_metrics_for_debate(debate_uuid)
        participant_metrics = self._repository.get_participant_metrics_for_debate(debate_uuid)
        pid_to_model = {str(p.id): p.model_name for p in participants}

        agreement_score: float | None = None
        for m in debate_metrics:
            if m.metric_name == "agreement_score":
                agreement_score = m.metric_value

        opinion_drifts: dict[str, float] = {}
        confidence_shifts: dict[str, float] = {}
        for pm in participant_metrics:
            key = pid_to_model.get(str(pm.participant_id), str(pm.participant_id))
            if pm.metric_name == "opinion_drift":
                opinion_drifts[key] = pm.metric_value
            elif pm.metric_name == "confidence_shift":
                confidence_shifts[key] = pm.metric_value

        transcript_metrics: TranscriptMetricsInfo | None = None
        if agreement_score is not None or opinion_drifts or confidence_shifts:
            transcript_metrics = TranscriptMetricsInfo(
                agreement_score=agreement_score,
                opinion_drifts=opinion_drifts,
                confidence_shifts=confidence_shifts,
            )

        return Transcript(
            debate_id=str(debate.id),
            question=debate.question,
            status=debate.status,
            participants=transcript_participants,
            rounds=transcript_rounds,
            consensus=transcript_consensus,
            metrics=transcript_metrics,
            created_at=debate.created_at,
            completed_at=debate.completed_at,
        )
