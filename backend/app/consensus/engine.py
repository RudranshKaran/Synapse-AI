"""ConsensusEngine — consensus generation from revised positions.

Two strategies depending on configuration:
1. LLM-based: Uses the Gemini provider for nuanced consensus analysis.
   This is the production default.
2. Deterministic: Falls back to sentence-level overlap analysis when
   no provider is available (testing, mock mode).
"""

from dataclasses import dataclass, field

from app.providers.base import ModelResponse


@dataclass
class ConsensusResult:
    """Output of the consensus generation process."""

    consensus_score: float
    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    summary: str = ""


class ConsensusEngine:
    """Generates consensus from a set of revised positions.

    Accepts an optional LLM provider. When provided, uses it for
    intelligent consensus analysis. Otherwise falls back to
    deterministic sentence-level overlap.
    """

    def __init__(self, consensus_provider=None) -> None:
        """Initialize with an optional consensus provider.

        Args:
            consensus_provider: A provider (e.g. GeminiProvider) used to
                generate LLM-based consensus. If None, uses deterministic
                overlap analysis.
        """
        self._provider = consensus_provider

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

        # Prefer LLM-based consensus when provider is available
        if self._provider is not None:
            try:
                return self._generate_with_llm(revised_positions)
            except Exception:
                # Fall through to deterministic on any LLM failure
                pass

        return self._generate_deterministic(revised_positions)

    # ── LLM-based strategy ────────────────────────────────

    def _generate_with_llm(self, revised_positions: list[dict]) -> ConsensusResult:
        """Use the LLM provider to generate consensus."""
        positions_text = ""
        for pos in revised_positions:
            positions_text += (
                f"--- {pos.get('model_name', 'unknown')} (Participant "
                f"{pos['participant_id'][:8]}... | Confidence: "
                f"{pos.get('confidence_score', 'N/A')}) ---\n"
                f"{pos['content']}\n\n"
            )

        # Use the provider's generate_response as a consensus prompt
        response: ModelResponse = self._provider.generate_response(
            question=(
                "Analyze the following debate positions and produce a consensus report. "
                "Identify key agreements, disagreements, assign a consensus score (0-100), "
                "and write a brief summary. Format your response as follows:\n\n"
                "Consensus Score: <score>\n"
                "Agreements:\n- <agreement 1>\n- <agreement 2>\n\n"
                "Disagreements:\n- <disagreement 1>\n- <disagreement 2>\n\n"
                "Summary:\n<summary text>"
            ),
            context=f"Debate Positions:\n\n{positions_text}",
        )

        return self._parse_llm_response(response.content)

    @staticmethod
    def _parse_llm_response(content: str) -> ConsensusResult:
        """Parse the LLM's structured consensus response."""
        import re

        score = 50.0
        agreements = []
        disagreements = []
        summary = ""

        # Extract score
        score_match = re.search(r"Consensus Score:\s*(\d{1,3}(?:\.\d+)?)", content)
        if score_match:
            score = min(max(float(score_match.group(1)), 0.0), 100.0)

        # Extract agreements section
        agree_section = re.search(
            r"Agreements:\s*(.*?)(?=Disagreements:|Summary:|$)",
            content,
            re.DOTALL,
        )
        if agree_section:
            agreements = [
                line.strip().lstrip("- ").strip()
                for line in agree_section.group(1).strip().split("\n")
                if line.strip().startswith("-")
            ]

        # Extract disagreements section
        disagree_section = re.search(
            r"Disagreements:\s*(.*?)(?=Summary:|$)",
            content,
            re.DOTALL,
        )
        if disagree_section:
            disagreements = [
                line.strip().lstrip("- ").strip()
                for line in disagree_section.group(1).strip().split("\n")
                if line.strip().startswith("-")
            ]

        # Extract summary
        summary_match = re.search(r"Summary:\s*(.*)", content, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()

        return ConsensusResult(
            consensus_score=score,
            agreements=agreements if agreements else ["No explicit agreements found."],
            disagreements=disagreements if disagreements else ["No explicit disagreements found."],
            summary=summary or f"Consensus score of {score}. "
            f"{len(agreements)} agreements and {len(disagreements)} disagreements identified.",
        )

    # ── Deterministic fallback strategy ────────────────────

    def _generate_deterministic(self, revised_positions: list[dict]) -> ConsensusResult:
        """Fallback: sentence-level overlap analysis."""
        import re

        position_sentences: list[list[str]] = []
        for pos in revised_positions:
            sentences = self._extract_sentences(pos["content"])
            position_sentences.append(sentences)

        common_normalized = self._find_common_sentences(position_sentences)

        agreements = []
        for norm_sent in common_normalized:
            for sentences in position_sentences:
                for s in sentences:
                    if self._normalize(s) == norm_sent:
                        agreements.append(s)
                        break
                if agreements and len(agreements) == len(common_normalized):
                    break

        disagreements = self._find_partial_sentences(position_sentences, common_normalized)

        total_unique = self._count_unique_sentences(position_sentences)
        shared_count = len(common_normalized)
        score = round((shared_count / total_unique) * 100, 1) if total_unique > 0 else 50.0

        summary = (
            f"Consensus score of {score}% indicates "
            f"{'strong consensus' if score >= 80 else 'moderate consensus' if score >= 60 else 'polarized debate' if score >= 40 else 'significant divergence'} "
            f"across {len(revised_positions)} participants. "
            f"{len(agreements)} common points identified, "
            f"{len(disagreements)} areas of divergence remain."
        )

        return ConsensusResult(
            consensus_score=score,
            agreements=agreements if agreements else ["No explicit agreements found."],
            disagreements=disagreements if disagreements else ["No explicit disagreements found."],
            summary=summary,
        )

    # ── Reusable helpers ──────────────────────────────────

    @staticmethod
    def _extract_sentences(text: str) -> list[str]:
        import re
        raw = re.split(r"(?:\.\s*|\n\s*)", text)
        return [s.strip() for s in raw if s.strip()]

    @staticmethod
    def _normalize(text: str) -> str:
        import re
        normalized = text.lower().strip()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    @staticmethod
    def _find_common_sentences(position_sentences: list[list[str]]) -> set[str]:
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
        all_sentences: set[str] = set()
        for sentences in position_sentences:
            for s in sentences:
                all_sentences.add(ConsensusEngine._normalize(s))
        partial_normalized = all_sentences - common_normalized
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
        unique: set[str] = set()
        for sentences in position_sentences:
            for s in sentences:
                unique.add(ConsensusEngine._normalize(s))
        return len(unique)
