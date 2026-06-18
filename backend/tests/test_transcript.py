"""Tests for the debate transcript endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.debate_round import DebateRound
from app.database.models.response import Response
from app.database.models.response_relationship import ResponseRelationship


CREATE_PAYLOAD = {
    "question": "Should AI code be deployed to production?",
    "models": ["model-a", "model-b", "model-c"],
}
RUN_PAYLOAD = {"rounds": 1}


def create_and_run(client: TestClient) -> str:
    did = client.post("/api/v1/debates", json=CREATE_PAYLOAD).json()["debate_id"]
    client.post(f"/api/v1/debates/{did}/run", json=RUN_PAYLOAD)
    return did


class TestTranscriptEndpoint:
    """Tests for GET /api/v1/debates/{debate_id}/transcript."""

    def test_transcript_returns_200(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.status_code == 200

    def test_transcript_has_debate_id(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.json()["debate_id"] == did

    def test_transcript_has_question(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.json()["question"] == CREATE_PAYLOAD["question"]

    def test_transcript_has_status(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.json()["status"] == "evaluation_complete"

    def test_transcript_has_participants(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert len(resp.json()["participants"]) == 3

    def test_transcript_has_rounds(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert len(resp.json()["rounds"]) == 5
        phases = [r["phase"] for r in resp.json()["rounds"]]
        assert phases == ["opinion", "critique", "revision", "consensus", "evaluation"]

    def test_transcript_rounds_have_responses(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        for r in resp.json()["rounds"]:
            assert "responses" in r
            assert isinstance(r["responses"], list)

    def test_transcript_opinion_round_has_three_responses(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        opinion_round = resp.json()["rounds"][0]
        assert opinion_round["phase"] == "opinion"
        assert len(opinion_round["responses"]) == 3

    def test_transcript_response_has_relationships(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        critique_round = resp.json()["rounds"][1]
        for entry in critique_round["responses"]:
            assert "relationships" in entry
            if entry["response_type"] == "critique":
                assert len(entry["relationships"]) == 1

    def test_transcript_has_consensus(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        c = resp.json()["consensus"]
        assert c is not None
        assert "consensus_score" in c
        assert "agreements" in c
        assert "disagreements" in c
        assert "summary" in c

    def test_transcript_has_metrics(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        m = resp.json()["metrics"]
        assert m is not None
        assert "agreement_score" in m
        assert "opinion_drifts" in m
        assert "confidence_shifts" in m

    def test_transcript_has_timestamps(self, client: TestClient) -> None:
        did = create_and_run(client)
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.json()["created_at"] is not None
        assert resp.json()["completed_at"] is not None

    def test_transcript_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000/transcript")
        assert resp.status_code == 404

    def test_transcript_invalid_uuid(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/not-a-uuid/transcript")
        assert resp.status_code == 400


class TestTranscriptNoExecution:
    """Transcript for a debate that hasn't been executed yet."""

    def test_transcript_without_execution(self, client: TestClient) -> None:
        did = client.post(
            "/api/v1/debates", json=CREATE_PAYLOAD
        ).json()["debate_id"]
        resp = client.get(f"/api/v1/debates/{did}/transcript")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "created"
        assert len(data["rounds"]) == 0
        assert data["consensus"] is None
        assert data["metrics"] is None
