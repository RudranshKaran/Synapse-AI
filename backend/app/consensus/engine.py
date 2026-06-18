"""ConsensusEngine — deterministic consensus generation from revised positions.

Generates a consensus artifact (score, agreements, disagreements, summary)
from the final revised positions of all debate participants. Designed to be
extensible — the initial implementation uses sentence-level overlap analysis,
but the interface supports swapping in embedding-based or LLM-based strategies.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ConsensusResult:
    """Output of the consensus generation process."""

    consensus_score: float
    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    summary: str = ""


class ConsensusEngine:
    """Generates consensus from a set of revised positions.

    The current implementation uses deterministic sentence-level overlap
    analysis. Future versions may use embedding similarity (Sentence
    Transformers) or LLM-as-a-judge for more nuanced consensus detection.
    """

    def generate(
        self,
        revised_positions: list[dict],
    ) -> ConsensusResult:
        """Generate a consensus artifact from revised positions.

        Args:
            revised_positions: List of dicts, each containing:
                participant_id, model_name, content, confidence_score.

        Returns:
            ConsensusResult with score, agreements, disagreements, summary.
        """
        if not revised_positions:
            return ConsensusResult(
                consensus_score=0.0,
                agreements=[],
                disagreements=[],
                summary="No positions to analyze.",
            )

        if len(revised_positions) == 1:
            return ConsensusResult(
                consensus_score=100.0,
                agreements=["Single position — full agreement by default."],
                disagreements=[],
                summary="Only one participant; consensus is trivially complete.",
            )

        # Extract sentences from each position
        position_sentences: list[list[str]] = []
        for pos in revised_positions:
            sentences = self._extract_sentences(pos["content"])
            position_sentences.append(sentences)

        # Find agreements: sentences that appear (normalized) in ALL positions
        common_normalized = self._find_common_sentences(position_sentences)

        agreements = []
        for norm_sent in common_normalized:
            # Use the first occurrence as the canonical form
            for sentences in position_sentences:
                for s in sentences:
                    if self._normalize(s) == norm_sent:
                        agreements.append(s)
                        break
                if agreements and len(agreements) == len(common_normalized):
                    break

        # Find disagreements: sentences that appear in SOME but not all positions
        disagreements = self._find_partial_sentences(position_sentences, common_normalized)

        # Calculate consensus score based on shared content ratio
        total_unique = self._count_unique_sentences(position_sentences)
        shared_count = len(common_normalized)
        if total_unique > 0:
            score = round((shared_count / total_unique) * 100, 1)
        else:
            score = 50.0  # Default middle value when no sentences can be compared

        # Generate summary
        summary = self._generate_summary(score, len(revised_positions), agreements, disagreements)

        return ConsensusResult(
            consensus_score=score,
            agreements=agreements if agreements else ["No explicit agreements found."],
            disagreements=disagreements if disagreements else ["No explicit disagreements found."],
            summary=summary,
        )

    # ── Private helpers ────────────────────────────────────

    @staticmethod
    def _extract_sentences(text: str) -> list[str]:
        """Split text into trimmed, non-empty sentences."""
        raw = re.split(r"(?:\.\s*|\n\s*)", text)
        return [s.strip() for s in raw if s.strip()]

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for comparison: lowercase, strip, remove punctuation."""
        normalized = text.lower().strip()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    @staticmethod
    def _find_common_sentences(position_sentences: list[list[str]]) -> set[str]:
        """Find normalized sentences present in ALL positions."""
        if not position_sentences:
            return set()

        sentence_sets = [
            {ConsensusEngine._normalize(s) for s in sentences}
            for sentences in position_sentences
        ]

        common = sentence_sets[0]
        for s in sentence_sets[1:]:
            common = common & s
        return common

    @staticmethod
    def _find_partial_sentences(
        position_sentences: list[list[str]],
        common_normalized: set[str],
    ) -> list[str]:
        """Find sentences present in some but not all positions."""
        all_sentences: set[str] = set()
        for sentences in position_sentences:
            for s in sentences:
                all_sentences.add(ConsensusEngine._normalize(s))

        partial_normalized = all_sentences - common_normalized
        # Convert back — use first occurrence text
        seen: set[str] = set()
        result: list[str] = []
        for sentences in position_sentences:
            for s in sentences:
                norm = ConsensusEngine._normalize(s)
                if norm in partial_normalized and norm not in seen:
                    seen.add(norm)
                    result.append(s)
        return result

    @staticmethod
    def _count_unique_sentences(position_sentences: list[list[str]]) -> int:
        """Count unique normalized sentences across all positions."""
        unique: set[str] = set()
        for sentences in position_sentences:
            for s in sentences:
                unique.add(ConsensusEngine._normalize(s))
        return len(unique)

    @staticmethod
    def _generate_summary(
        score: float, num_participants: int, agreements: list[str], disagreements: list[str]
    ) -> str:
        """Generate a human-readable summary of the consensus."""
        if score >= 80:
            level = "strong consensus"
        elif score >= 60:
            level = "moderate consensus"
        elif score >= 40:
            level = "polarized debate"
        else:
            level = "significant divergence"

        agree_count = len(agreements)
        disagree_count = len(disagreements)

        return (
            f"Consensus score of {score}% indicates {level} "
            f"across {num_participants} participants. "
            f"{agree_count} common points identified, "
            f"{disagree_count} areas of divergence remain."
        )
