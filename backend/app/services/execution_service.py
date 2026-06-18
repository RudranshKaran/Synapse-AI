"""Debate execution service — orchestrates the debate lifecycle.

Implements the full pipeline: opinion generation, critique, revision,
consensus, and evaluation. Each phase is a separate logical step.
"""

import uuid
from datetime import datetime

from fastapi import HTTPException, status

from app.consensus.engine import ConsensusEngine, ConsensusResult as EngineResult
from app.core.logging import get_logger
from app.evaluation.engine import EvaluationEngine
from app.providers.factory import create_provider
from app.repositories.debate_repository import DebateRepository
from app.schemas.execution import (
    ConsensusResult,
    DebateRunRequest,
    DebateRunResponse,
    CritiqueResult,
    EvaluationResult,
    OpinionResult,
    RevisionResult,
)
from app.services.debate_state import (
    ConsensusRecord,
    CritiqueRecord,
    DebateState,
    EvaluationRecord,
    OpinionRecord,
    RevisionRecord,
)

logger = get_logger(__name__)


class ExecutionService:
    """Service for debate execution and orchestration.

    Each phase of the debate lifecycle maps to a method on this service.
    Currently implements: opinion_generation, critique_phase.
    Future: revision, consensus, evaluation.
    """

    def __init__(
        self,
        repository: DebateRepository,
        consensus_engine: ConsensusEngine | None = None,
        evaluation_engine: EvaluationEngine | None = None,
    ) -> None:
        self._repository = repository
        self._consensus_engine = consensus_engine or ConsensusEngine()
        self._evaluation_engine = evaluation_engine or EvaluationEngine()

    def run_opinion_generation(
        self, debate_id: str, payload: DebateRunRequest
    ) -> DebateRunResponse:
        """Execute the opinion generation phase only.

        This is kept as a public method for backward compatibility
        and independent phase execution. For the full pipeline
        (opinions + critiques), use run_debate().

        Workflow:
        1. Load debate and participants from database.
        2. Resolve providers via the factory.
        3. Generate opinions from each participant.
        4. Create debate_round record and persist responses.
        5. Update debate status.
        6. Return generated opinions.

        Args:
            debate_id: The debate UUID as a string.
            payload: Validated run request.

        Returns:
            DebateRunResponse with status and generated opinions.

        Raises:
            HTTPException: If debate not found or execution fails.
        """
        debate_uuid, debate, participants = self._load_debate(debate_id)

        # Create round for opinion generation
        debate_round = self._repository.create_round(
            debate_id=debate_uuid,
            round_number=1,
            phase="opinion",
        )

        self._repository.update_debate_status(debate_uuid, "running")

        # Generate opinions from each participant
        opinion_results: list[OpinionResult] = []
        for participant in participants:
            provider = self._resolve_provider(participant)
            model_response = provider.generate_response(question=debate.question)

            stored = self._repository.create_response(
                debate_id=debate_uuid,
                round_id=debate_round.id,
                participant_id=participant.id,
                response_type="opinion",
                content=model_response.content,
                confidence_score=model_response.confidence,
            )

            opinion_results.append(
                OpinionResult(
                    participant_id=str(participant.id),
                    model_name=participant.model_name,
                    content=model_response.content,
                    confidence_score=model_response.confidence,
                )
            )

        self._repository.update_debate_status(debate_uuid, "opinions_generated")

        return DebateRunResponse(
            debate_id=str(debate.id),
            status="opinions_generated",
            opinions=opinion_results,
        )

    def run_debate(self, debate_id: str, payload: DebateRunRequest) -> DebateRunResponse:
        """Execute the full debate pipeline: opinions → critiques → revisions.

        Runs all phases sequentially and returns a combined response
        with opinions, critiques, and revisions. Future phases
        (consensus, evaluation) will be added here.

        Args:
            debate_id: The debate UUID as a string.
            payload: Validated run request.

        Returns:
            DebateRunResponse with status, opinions, critiques, and revisions.
        """
        debate_uuid, debate, participants = self._load_debate(debate_id)

        # === Phase 1: Opinion Generation ===
        opinion_round = self._repository.create_round(
            debate_id=debate_uuid, round_number=1, phase="opinion",
        )

        self._repository.update_debate_status(debate_uuid, "running")

        opinion_results: list[OpinionResult] = []
        stored_opinions: list[tuple] = []  # (participant, response_id, opinion_result)

        for participant in participants:
            provider = self._resolve_provider(participant)
            model_response = provider.generate_response(question=debate.question)

            stored = self._repository.create_response(
                debate_id=debate_uuid,
                round_id=opinion_round.id,
                participant_id=participant.id,
                response_type="opinion",
                content=model_response.content,
                confidence_score=model_response.confidence,
            )

            result = OpinionResult(
                participant_id=str(participant.id),
                model_name=participant.model_name,
                content=model_response.content,
                confidence_score=model_response.confidence,
            )
            opinion_results.append(result)
            stored_opinions.append((participant, stored.id, result))

        # === Phase 2: Critique Generation ===
        critique_round = self._repository.create_round(
            debate_id=debate_uuid, round_number=2, phase="critique",
        )

        critique_results: list[CritiqueResult] = []
        # Track which critiques target each opinion: opinion_response_id → list of (critic_participant, critique_content)
        critiques_by_target: dict[uuid.UUID, list[tuple]] = {}
        participant_count = len(participants)

        for i, (participant, _, _) in enumerate(stored_opinions):
            target_idx = (i + 1) % participant_count
            target_participant, target_response_id, target_opinion = stored_opinions[target_idx]

            provider = self._resolve_provider(participant)
            model_response = provider.critique_response(
                question=debate.question,
                response=target_opinion.content,
            )

            stored_critique = self._repository.create_response(
                debate_id=debate_uuid,
                round_id=critique_round.id,
                participant_id=participant.id,
                response_type="critique",
                content=model_response.content,
                confidence_score=model_response.confidence,
            )

            # Create the relationship linking critique → target opinion
            self._repository.create_response_relationship(
                source_response_id=stored_critique.id,
                target_response_id=target_response_id,
                relationship_type="critiques",
            )

            critique_results.append(
                CritiqueResult(
                    participant_id=str(participant.id),
                    model_name=participant.model_name,
                    content=model_response.content,
                    confidence_score=model_response.confidence,
                    target_participant_id=str(target_participant.id),
                    target_model_name=target_participant.model_name,
                )
            )

            # Track for revision phase
            critiques_by_target.setdefault(target_response_id, []).append(
                (participant, model_response.content)
            )

        # === Phase 3: Revision Generation ===
        revision_round = self._repository.create_round(
            debate_id=debate_uuid, round_number=3, phase="revision",
        )

        revision_results: list[RevisionResult] = []

        for participant, opinion_response_id, opinion_result in stored_opinions:
            # Find all critiques targeting this participant's opinion
            target_critiques = critiques_by_target.get(opinion_response_id, [])

            # Combine all critiques into a single string for the provider
            critique_texts = [c[1] for c in target_critiques]
            combined_critiques = "\n\n".join(critique_texts)

            provider = self._resolve_provider(participant)
            model_response = provider.revise_position(
                question=debate.question,
                original_response=opinion_result.content,
                critique=combined_critiques,
            )

            stored_revision = self._repository.create_response(
                debate_id=debate_uuid,
                round_id=revision_round.id,
                participant_id=participant.id,
                response_type="revision",
                content=model_response.content,
                confidence_score=model_response.confidence,
            )

            # Create the relationship linking revision → original opinion
            self._repository.create_response_relationship(
                source_response_id=stored_revision.id,
                target_response_id=opinion_response_id,
                relationship_type="revises",
            )

            revision_results.append(
                RevisionResult(
                    participant_id=str(participant.id),
                    model_name=participant.model_name,
                    content=model_response.content,
                    confidence_score=model_response.confidence,
                    original_participant_id=str(participant.id),
                    original_model_name=participant.model_name,
                )
            )

        # === Phase 4: Consensus Generation ===
        consensus_round = self._repository.create_round(
            debate_id=debate_uuid, round_number=4, phase="consensus",
        )

        # Build revised positions for the consensus engine
        revised_positions = [
            {
                "participant_id": str(p.id),
                "model_name": p.model_name,
                "content": r.content,
                "confidence_score": r.confidence_score,
            }
            for (p, _, _), r in zip(stored_opinions, revision_results)
        ]

        engine_result: EngineResult = self._consensus_engine.generate(
            revised_positions=revised_positions,
        )

        # Persist consensus report
        report = self._repository.create_consensus_report(
            debate_id=debate_uuid,
            consensus_score=engine_result.consensus_score,
            summary=engine_result.summary,
        )

        # Persist individual agreements and disagreements
        for agreement_text in engine_result.agreements:
            self._repository.create_consensus_item(
                consensus_report_id=report.id,
                item_type="agreement",
                content=agreement_text,
            )

        for disagreement_text in engine_result.disagreements:
            self._repository.create_consensus_item(
                consensus_report_id=report.id,
                item_type="disagreement",
                content=disagreement_text,
            )

        consensus_schema = ConsensusResult(
            consensus_score=engine_result.consensus_score,
            agreements=engine_result.agreements,
            disagreements=engine_result.disagreements,
            summary=engine_result.summary,
        )

        # === Phase 5: Evaluation ===
        evaluation_round = self._repository.create_round(
            debate_id=debate_uuid, round_number=5, phase="evaluation",
        )

        # Build data structures for evaluation engine
        opinion_data = [
            {
                "participant_id": str(p.id),
                "content": o.content,
                "confidence_score": o.confidence_score,
            }
            for (p, _, o) in stored_opinions
        ]
        revision_data = [
            {
                "participant_id": str(p.id),
                "content": r.content,
                "confidence_score": r.confidence_score,
            }
            for (p, _, _), r in zip(stored_opinions, revision_results)
        ]
        participant_data = [
            {"id": str(p.id), "model_name": p.model_name} for p in participants
        ]

        eval_engine_result = self._evaluation_engine.evaluate(
            opinions=opinion_data,
            revisions=revision_data,
            participants=participant_data,
        )

        # Persist debate-level metric
        self._repository.create_evaluation_metric(
            debate_id=debate_uuid,
            metric_name="agreement_score",
            metric_value=eval_engine_result.agreement_score,
        )

        # Persist participant-level metrics
        for pid, drift in eval_engine_result.opinion_drifts.items():
            self._repository.create_participant_metric(
                debate_id=debate_uuid,
                participant_id=uuid.UUID(pid),
                metric_name="opinion_drift",
                metric_value=drift,
            )

        for pid, shift in eval_engine_result.confidence_shifts.items():
            self._repository.create_participant_metric(
                debate_id=debate_uuid,
                participant_id=uuid.UUID(pid),
                metric_name="confidence_shift",
                metric_value=shift,
            )

        evaluation_schema = EvaluationResult(
            agreement_score=eval_engine_result.agreement_score,
            opinion_drifts=eval_engine_result.opinion_drifts,
            confidence_shifts=eval_engine_result.confidence_shifts,
        )

        self._repository.update_debate_status(
            debate_uuid, "evaluation_complete",
            completed_at=datetime.now(),
        )

        return DebateRunResponse(
            debate_id=str(debate.id),
            status="evaluation_complete",
            opinions=opinion_results,
            critiques=critique_results,
            revisions=revision_results,
            consensus=consensus_schema,
            evaluation=evaluation_schema,
        )

    # ── Private helpers ────────────────────────────────────

    def _load_debate(self, debate_id: str) -> tuple:
        """Load debate and participants, raising on errors.

        Returns:
            Tuple of (debate_uuid, debate, participants).
        """
        debate_uuid = self._validate_uuid(debate_id)
        debate = self._repository.get_debate_by_id(debate_uuid)
        if debate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate not found: {debate_id}",
            )

        participants = self._repository.get_participants_for_debate(debate_uuid)
        if not participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debate has no participants",
            )

        return debate_uuid, debate, participants

    @staticmethod
    def _resolve_provider(participant):
        """Resolve a provider for a participant, raising on failure."""
        provider = create_provider(participant.model_name)
        if provider is None:
            logger.warning(
                "No provider found for model %s (participant %s)",
                participant.model_name,
                participant.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unsupported model: {participant.model_name}",
            )
        return provider

    @staticmethod
    def _validate_uuid(debate_id: str) -> uuid.UUID:
        """Validate and parse a UUID string.

        Args:
            debate_id: The UUID string to validate.

        Returns:
            Parsed UUID.

        Raises:
            HTTPException: If the string is not a valid UUID.
        """
        try:
            return uuid.UUID(debate_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid debate ID format: {debate_id}",
            )
