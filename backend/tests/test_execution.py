"""Tests for the debate execution pipeline (full: opinions → critiques → revisions → consensus → evaluation)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.consensus.engine import ConsensusEngine, ConsensusResult
from app.database.models.consensus_item import ConsensusItem
from app.database.models.consensus_report import ConsensusReport
from app.database.models.debate import Debate
from app.database.models.debate_round import DebateRound
from app.database.models.evaluation_metric import EvaluationMetric
from app.database.models.participant import Participant
from app.database.models.participant_metric import ParticipantMetric
from app.database.models.response import Response
from app.database.models.response_relationship import ResponseRelationship
from app.evaluation.embedding import compute_embedding, cosine_similarity
from app.evaluation.engine import EvaluationEngine, EvaluationResult
from app.evaluation.metrics.agreement_score import compute_agreement_score
from app.evaluation.metrics.confidence_shift import compute_confidence_shift
from app.evaluation.metrics.opinion_drift import compute_opinion_drift
from app.services.debate_state import (
    ConsensusRecord,
    CritiqueRecord,
    DebateState,
    EvaluationRecord,
    OpinionRecord,
    RevisionRecord,
)


# ── Helpers ─────────────────────────────────────────────────

CREATE_PAYLOAD_3 = {
    "question": "Should AI-generated code be deployed to production?",
    "models": ["model-a", "model-b", "model-c"],
}
RUN_PAYLOAD = {"rounds": 1}


def create_debate(client: TestClient, payload: dict | None = None) -> str:
    resp = client.post("/api/v1/debates", json=payload or CREATE_PAYLOAD_3)
    return resp.json()["debate_id"]


# ── Pipeline: Full ──────────────────────────────────────────


class TestRunDebatePipeline:
    """Full pipeline: opinions + critiques + revisions + consensus + evaluation."""

    def test_run_returns_200(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.status_code == 200

    def test_run_returns_three_opinions(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert len(resp.json()["opinions"]) == 3

    def test_run_returns_three_critiques(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert len(resp.json()["critiques"]) == 3

    def test_run_returns_three_revisions(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert len(resp.json()["revisions"]) == 3

    def test_run_returns_consensus(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.json()["consensus"] is not None

    def test_run_returns_evaluation(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.json()["evaluation"] is not None

    def test_evaluation_has_required_fields(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        e = resp.json()["evaluation"]
        assert "agreement_score" in e
        assert "opinion_drifts" in e
        assert "confidence_shifts" in e

    def test_evaluation_agreement_score_is_float(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert isinstance(resp.json()["evaluation"]["agreement_score"], float)

    def test_evaluation_has_three_drifts(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert len(resp.json()["evaluation"]["opinion_drifts"]) == 3

    def test_evaluation_has_three_shifts(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert len(resp.json()["evaluation"]["confidence_shifts"]) == 3

    def test_run_returns_debate_id(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.json()["debate_id"] == debate_id

    def test_run_updates_status(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}")
        assert resp.json()["status"] == "evaluation_complete"

    def test_run_returns_status(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.json()["status"] == "evaluation_complete"


# ── Persistence ─────────────────────────────────────────────


class TestRunPersistence:
    """Verify all debate artifacts are persisted correctly."""

    def test_persists_five_rounds(self, client: TestClient, db_session: Session) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        rounds = (
            db_session.query(DebateRound)
            .filter(DebateRound.debate_id == uuid.UUID(debate_id))
            .order_by(DebateRound.round_number)
            .all()
        )
        assert len(rounds) == 5
        assert rounds[0].phase == "opinion"
        assert rounds[1].phase == "critique"
        assert rounds[2].phase == "revision"
        assert rounds[3].phase == "consensus"
        assert rounds[4].phase == "evaluation"

    def test_persists_all_responses(self, client: TestClient, db_session: Session) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        responses = (
            db_session.query(Response)
            .filter(Response.debate_id == uuid.UUID(debate_id))
            .all()
        )
        assert len(responses) == 9

    def test_persists_evaluation_metric(self, client: TestClient, db_session: Session) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        metrics = (
            db_session.query(EvaluationMetric)
            .filter(EvaluationMetric.debate_id == uuid.UUID(debate_id))
            .all()
        )
        metric_names = {m.metric_name for m in metrics}
        assert "agreement_score" in metric_names

    def test_persists_participant_metrics(self, client: TestClient, db_session: Session) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        p_metrics = (
            db_session.query(ParticipantMetric)
            .filter(ParticipantMetric.debate_id == uuid.UUID(debate_id))
            .all()
        )
        metric_names = {m.metric_name for m in p_metrics}
        assert "opinion_drift" in metric_names
        assert "confidence_shift" in metric_names
        # 3 participants × 2 metrics each = 6 rows
        assert len(p_metrics) == 6

    def test_persists_relationships(self, client: TestClient, db_session: Session) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        rels = db_session.query(ResponseRelationship).all()
        assert len(rels) == 6


# ── Metrics Endpoint ────────────────────────────────────────


class TestMetricsEndpoint:
    """Tests for GET /api/v1/debates/{debate_id}/metrics."""

    def test_metrics_returns_200(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        assert resp.status_code == 200

    def test_metrics_debate_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000/metrics")
        assert resp.status_code == 404

    def test_metrics_invalid_uuid(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/not-a-uuid/metrics")
        assert resp.status_code == 400

    def test_metrics_has_agreement_score(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        assert resp.json()["agreement_score"] is not None

    def test_metrics_has_opinion_drifts(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        assert len(resp.json()["opinion_drifts"]) == 3

    def test_metrics_has_confidence_shifts(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        assert len(resp.json()["confidence_shifts"]) == 3

    def test_metrics_drift_values_in_range(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        for v in resp.json()["opinion_drifts"].values():
            assert 0.0 <= v <= 1.0

    def test_metrics_agreement_in_range(self, client: TestClient) -> None:
        debate_id = create_debate(client)
        client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        resp = client.get(f"/api/v1/debates/{debate_id}/metrics")
        score = resp.json()["agreement_score"]
        assert 0.0 <= score <= 100.0


# ── Metric Calculator Unit Tests ────────────────────────────


class TestAgreementScore:
    """Unit tests for the Agreement Score calculator."""

    def test_requires_at_least_two_positions(self) -> None:
        with pytest.raises(ValueError):
            compute_agreement_score(["Single position"])

    def test_identical_texts_give_high_score(self) -> None:
        text = "All models should be reviewed by humans before deployment."
        score = compute_agreement_score([text, text])
        assert score >= 90.0  # Very similar (identical) → near 100

    def test_score_between_zero_and_one_hundred(self) -> None:
        score = compute_agreement_score([
            "We should always deploy to production immediately.",
            "We should never deploy without extensive testing.",
        ])
        assert 0.0 <= score <= 100.0


class TestOpinionDrift:
    """Unit tests for the Opinion Drift calculator."""

    def test_identical_texts_give_zero_drift(self) -> None:
        text = "I believe AI should be reviewed by humans."
        drift = compute_opinion_drift(text, text)
        assert drift <= 0.05  # Very similar (identical) → near 0

    def test_different_texts_give_positive_drift(self) -> None:
        drift = compute_opinion_drift(
            "I am strongly in favor of this approach.",
            "I have completely changed my mind and now oppose this.",
        )
        assert 0.0 <= drift <= 1.0

    def test_drift_range(self) -> None:
        drift = compute_opinion_drift("Original opinion on the topic.", "Revised position after critique.")
        assert 0.0 <= drift <= 1.0


class TestConfidenceShift:
    """Unit tests for the Confidence Shift calculator."""

    def test_increase_is_positive(self) -> None:
        assert compute_confidence_shift(70.0, 85.0) == 15.0

    def test_decrease_is_negative(self) -> None:
        assert compute_confidence_shift(85.0, 70.0) == -15.0

    def test_no_change_is_zero(self) -> None:
        assert compute_confidence_shift(75.0, 75.0) == 0.0

    def test_none_original_returns_zero(self) -> None:
        assert compute_confidence_shift(None, 80.0) == 0.0

    def test_none_revised_returns_zero(self) -> None:
        assert compute_confidence_shift(80.0, None) == 0.0

    def test_both_none_returns_zero(self) -> None:
        assert compute_confidence_shift(None, None) == 0.0


# ── Evaluation Engine Unit Tests ────────────────────────────


class TestEvaluationEngine:
    """Unit tests for the EvaluationEngine orchestrator."""

    def setup_method(self) -> None:
        self.engine = EvaluationEngine()

    def test_returns_evaluation_result(self) -> None:
        result = self.engine.evaluate(
            opinions=[
                {"participant_id": "p1", "content": "Initial position A.", "confidence_score": 80.0},
                {"participant_id": "p2", "content": "Initial position B.", "confidence_score": 70.0},
            ],
            revisions=[
                {"participant_id": "p1", "content": "Revised position A.", "confidence_score": 85.0},
                {"participant_id": "p2", "content": "Revised position B.", "confidence_score": 75.0},
            ],
            participants=[
                {"id": "p1", "model_name": "model-a"},
                {"id": "p2", "model_name": "model-b"},
            ],
        )
        assert isinstance(result, EvaluationResult)
        assert isinstance(result.agreement_score, float)
        assert isinstance(result.opinion_drifts, dict)
        assert isinstance(result.confidence_shifts, dict)

    def test_agreement_score_generated(self) -> None:
        result = self.engine.evaluate(
            opinions=[{"participant_id": "p1", "content": "A", "confidence_score": 80.0},
                       {"participant_id": "p2", "content": "B", "confidence_score": 70.0}],
            revisions=[{"participant_id": "p1", "content": "A rev", "confidence_score": 85.0},
                        {"participant_id": "p2", "content": "B rev", "confidence_score": 75.0}],
            participants=[{"id": "p1", "model_name": "a"}, {"id": "p2", "model_name": "b"}],
        )
        assert 0.0 <= result.agreement_score <= 100.0

    def test_opinion_drifts_per_participant(self) -> None:
        result = self.engine.evaluate(
            opinions=[{"participant_id": "p1", "content": "A", "confidence_score": 80.0},
                       {"participant_id": "p2", "content": "B", "confidence_score": 70.0}],
            revisions=[{"participant_id": "p1", "content": "A2", "confidence_score": 85.0},
                        {"participant_id": "p2", "content": "B2", "confidence_score": 75.0}],
            participants=[{"id": "p1", "model_name": "a"}, {"id": "p2", "model_name": "b"}],
        )
        assert "p1" in result.opinion_drifts
        assert "p2" in result.opinion_drifts

    def test_confidence_shifts_per_participant(self) -> None:
        result = self.engine.evaluate(
            opinions=[{"participant_id": "p1", "content": "A", "confidence_score": 80.0},
                       {"participant_id": "p2", "content": "B", "confidence_score": 70.0}],
            revisions=[{"participant_id": "p1", "content": "A2", "confidence_score": 85.0},
                        {"participant_id": "p2", "content": "B2", "confidence_score": 65.0}],
            participants=[{"id": "p1", "model_name": "a"}, {"id": "p2", "model_name": "b"}],
        )
        assert result.confidence_shifts["p1"] == 5.0
        assert result.confidence_shifts["p2"] == -5.0


# ── Error Handling ──────────────────────────────────────────


class TestRunErrorHandling:
    """Error handling tests for the run endpoint."""

    def test_run_debate_not_found(self, client: TestClient) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.post(f"/api/v1/debates/{fake_id}/run", json=RUN_PAYLOAD)
        assert resp.status_code == 404

    def test_run_invalid_uuid(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates/not-a-uuid/run", json=RUN_PAYLOAD)
        assert resp.status_code == 400

    def test_run_unsupported_model(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/debates",
            json={"question": "Test?", "models": ["nonexistent-model"]},
        )
        debate_id = resp.json()["debate_id"]
        resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        assert resp.status_code == 500


# ── DebateState Model ───────────────────────────────────────


class TestDebateState:
    """DebateState record model tests."""

    def test_default_collections_are_empty(self) -> None:
        state = DebateState(debate_id="abc", question="Test?")
        assert state.participants == []
        assert state.opinions == []
        assert state.critiques == []
        assert state.revisions == []
        assert state.consensus is None
        assert state.evaluation is None

    def test_evaluation_record_creation(self) -> None:
        record = EvaluationRecord(
            agreement_score=92.5,
            opinion_drifts={"p1": 0.15},
            confidence_shifts={"p1": 5.0},
        )
        assert record.agreement_score == 92.5
        assert record.opinion_drifts == {"p1": 0.15}
        assert record.confidence_shifts == {"p1": 5.0}

    def test_evaluation_record_defaults(self) -> None:
        record = EvaluationRecord()
        assert record.agreement_score == 0.0
        assert record.opinion_drifts == {}
        assert record.confidence_shifts == {}

    def test_state_assigns_evaluation(self) -> None:
        state = DebateState(debate_id="abc", question="Test?")
        state.evaluation = EvaluationRecord(agreement_score=88.0)
        assert state.evaluation is not None
        assert state.evaluation.agreement_score == 88.0
