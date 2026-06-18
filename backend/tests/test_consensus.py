"""Tests for the ConsensusEngine — both deterministic and LLM-based strategies."""

from unittest.mock import MagicMock

from app.consensus.engine import ConsensusEngine, ConsensusResult


class TestConsensusEngineDeterministic:
    """Tests for the deterministic (sentence-overlap) consensus strategy."""

    def setup_method(self) -> None:
        self.engine = ConsensusEngine()

    def test_empty_positions(self) -> None:
        result = self.engine.generate([])
        assert result.consensus_score == 0.0
        assert "No positions" in result.summary

    def test_single_position(self) -> None:
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "I believe X is correct.", "confidence_score": 80.0},
        ]
        result = self.engine.generate(positions)
        assert result.consensus_score == 100.0
        assert len(result.agreements) > 0

    def test_two_positions_full_agreement(self) -> None:
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "I believe X is correct. Y follows from X.", "confidence_score": 80.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "I believe X is correct. Y follows from X.", "confidence_score": 75.0},
        ]
        result = self.engine.generate(positions)
        assert result.consensus_score == 100.0

    def test_two_positions_partial_agreement(self) -> None:
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "I believe X is correct. Y follows from X.", "confidence_score": 80.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "I believe X is correct. Z contradicts X.", "confidence_score": 75.0},
        ]
        result = self.engine.generate(positions)
        # They share "I believe X is correct" but differ on the second sentence
        assert result.consensus_score > 0
        assert result.consensus_score < 100
        assert len(result.agreements) > 0
        assert len(result.disagreements) > 0

    def test_three_positions(self) -> None:
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "Climate change is real. We need action.", "confidence_score": 90.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "Climate change is real. The cost is high.", "confidence_score": 80.0},
            {"participant_id": "p3", "model_name": "agent-c",
             "content": "Climate change is real. We need global cooperation.", "confidence_score": 85.0},
        ]
        result = self.engine.generate(positions)
        # All three agree on "Climate change is real."
        assert "Climate change is real" in result.agreements[0] or any(
            "Climate" in a for a in result.agreements
        )
        # 1 shared sentence out of 4 unique = 25%
        assert result.consensus_score == 25.0

    def test_different_model_names_dont_affect_score(self) -> None:
        """Consensus depends on content, not model names."""
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "X is true.", "confidence_score": 90.0},
            {"participant_id": "p2", "model_name": "gpt-4o",
             "content": "X is false.", "confidence_score": 85.0},
        ]
        result = self.engine.generate(positions)
        assert result.consensus_score == 0.0  # No overlapping sentences
        assert "No explicit agreements" in result.agreements[0]


class TestConsensusEngineLLM:
    """Tests for the LLM-based consensus strategy."""

    def test_uses_consensus_provider_when_available(self) -> None:
        provider = MagicMock()
        provider.generate_response.return_value.content = (
            "Consensus Score: 72\n\n"
            "Agreements:\n- Both support renewable energy\n"
            "- Both acknowledge climate urgency\n\n"
            "Disagreements:\n- Different timelines for action\n\n"
            "Summary:\nModerate agreement with some divergence on implementation."
        )
        provider.generate_response.return_value.confidence = 90.0

        engine = ConsensusEngine(consensus_provider=provider)
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "We need renewable energy now.", "confidence_score": 85.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "Renewable energy is important but costs matter.", "confidence_score": 75.0},
        ]
        result = engine.generate(positions)
        assert result.consensus_score == 72.0
        assert "renewable" in result.agreements[0].lower()
        assert len(result.disagreements) > 0
        assert "Moderate" in result.summary

    def test_falls_back_to_deterministic_on_provider_error(self) -> None:
        provider = MagicMock()
        provider.generate_response.side_effect = RuntimeError("API down")

        engine = ConsensusEngine(consensus_provider=provider)
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "X is correct.", "confidence_score": 80.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "X is correct.", "confidence_score": 75.0},
        ]
        result = engine.generate(positions)
        # Should fall back to deterministic and find full agreement
        assert result.consensus_score == 100.0

    def test_parse_llm_response_handles_missing_sections(self) -> None:
        engine = ConsensusEngine(consensus_provider=MagicMock())
        result = engine._parse_llm_response(
            "Consensus Score: 65\n\nSome text without clear sections."
        )
        assert result.consensus_score == 65.0
        assert len(result.agreements) > 0  # Has defaults
        assert len(result.disagreements) > 0

    def test_parse_llm_response_handles_no_score(self) -> None:
        engine = ConsensusEngine(consensus_provider=MagicMock())
        result = engine._parse_llm_response(
            "Agreements:\n- Item 1\n- Item 2\n\nSummary:\nA summary."
        )
        assert result.consensus_score == 50.0  # Default score
        assert len(result.agreements) == 2

    def test_provider_receives_all_positions(self) -> None:
        provider = MagicMock()
        provider.generate_response.return_value.content = (
            "Consensus Score: 80\n\nAgreements:\n- All agree\n\n"
            "Disagreements:\n- Minor diff\n\nSummary:\nDone."
        )

        engine = ConsensusEngine(consensus_provider=provider)
        positions = [
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "Position one.", "confidence_score": 80.0},
            {"participant_id": "p2", "model_name": "agent-b",
             "content": "Position two.", "confidence_score": 70.0},
            {"participant_id": "p3", "model_name": "agent-c",
             "content": "Position three.", "confidence_score": 90.0},
        ]
        engine.generate(positions)

        # Check that the provider was called with all positions
        call_args = provider.generate_response.call_args
        assert call_args is not None
        assert "Position one" in call_args[1].get("context", "")
        assert "Position three" in call_args[1].get("context", "")

    def test_should_not_use_provider_for_single_position(self) -> None:
        provider = MagicMock()
        engine = ConsensusEngine(consensus_provider=provider)
        result = engine.generate([
            {"participant_id": "p1", "model_name": "agent-a",
             "content": "Only position.", "confidence_score": 80.0},
        ])
        # Single position — should return trivially without calling provider
        provider.generate_response.assert_not_called()
        assert result.consensus_score == 100.0
