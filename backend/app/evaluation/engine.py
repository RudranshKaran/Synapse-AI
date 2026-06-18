"""EvaluationEngine — orchestrates all metric computations for a debate.

Coordinates the Agreement Score, Opinion Drift, and Confidence Shift
calculators. Designed to be extensible — new metrics can be added
as independent calculator functions and called from this engine.
"""

from dataclasses import dataclass, field


@dataclass
class EvaluationResult:
    """Complete evaluation output for a single debate."""

    agreement_score: float
    opinion_drifts: dict[str, float]  # participant_id → drift
    confidence_shifts: dict[str, float]  # participant_id → shift


class EvaluationEngine:
    """Orchestrates metric computation for a debate.

    The engine receives debate data (opinions, revisions, participants)
    and delegates to individual metric calculators. New metrics can be
    added by creating a calculator and calling it in evaluate().
    """

    def evaluate(
        self,
        opinions: list[dict],
        revisions: list[dict],
        participants: list[dict],
    ) -> EvaluationResult:
        """Run all evaluation metrics for a debate.

        Args:
            opinions: List of dicts with participant_id, content, confidence_score.
            revisions: List of dicts with participant_id, content, confidence_score.
            participants: List of dicts with id, model_name.

        Returns:
            EvaluationResult containing all computed metrics.
        """
        # Import calculators here to keep engine import-light
        from app.evaluation.metrics.agreement_score import compute_agreement_score
        from app.evaluation.metrics.confidence_shift import (
            compute_confidence_shift as calc_confidence_shift,
        )
        from app.evaluation.metrics.opinion_drift import (
            compute_opinion_drift as calc_opinion_drift,
        )

        # Build lookup maps
        opinions_by_participant = {o["participant_id"]: o for o in opinions}
        revisions_by_participant = {r["participant_id"]: r for r in revisions}

        # Agreement Score: all revised positions
        revised_texts = [r["content"] for r in revisions]
        agreement_score = (
            compute_agreement_score(revised_texts) if len(revised_texts) >= 2 else 100.0
        )

        # Per-participant metrics
        opinion_drifts: dict[str, float] = {}
        confidence_shifts: dict[str, float] = {}

        for participant in participants:
            pid = participant["id"]
            opinion = opinions_by_participant.get(pid)
            revision = revisions_by_participant.get(pid)

            if opinion and revision:
                # Opinion Drift
                drift = calc_opinion_drift(
                    original_text=opinion["content"],
                    revised_text=revision["content"],
                )
                opinion_drifts[pid] = drift

                # Confidence Shift
                shift = calc_confidence_shift(
                    original_confidence=opinion.get("confidence_score"),
                    revised_confidence=revision.get("confidence_score"),
                )
                confidence_shifts[pid] = shift

        return EvaluationResult(
            agreement_score=agreement_score,
            opinion_drifts=opinion_drifts,
            confidence_shifts=confidence_shifts,
        )
