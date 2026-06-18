"""Tests for debate CRUD endpoints and configuration."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.debate import Debate


class TestCreateDebate:
    """Debate creation test suite."""

    VALID_PAYLOAD = {
        "question": "Should AI-generated code be deployed directly to production?",
        "models": ["model-a", "model-b", "model-c"],
    }

    def test_create_debate_returns_201(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        assert resp.status_code == 201

    def test_create_debate_returns_expected_fields(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        data = resp.json()
        assert "debate_id" in data
        assert "question" in data
        assert "status" in data
        assert "participants" in data
        assert "created_at" in data

    def test_create_debate_default_status(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        assert resp.json()["status"] == "created"

    def test_create_debate_returns_uuid(self, client: TestClient) -> None:
        import uuid
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        uuid.UUID(resp.json()["debate_id"])

    def test_create_debate_persists_data(self, client: TestClient, db_session: Session) -> None:
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        import uuid
        debate = db_session.get(Debate, uuid.UUID(resp.json()["debate_id"]))
        assert debate is not None
        assert debate.question == self.VALID_PAYLOAD["question"]

    def test_create_debate_returns_participants(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=self.VALID_PAYLOAD)
        participants = resp.json()["participants"]
        assert len(participants) == 3
        for p in participants:
            assert "participant_id" in p
            assert "model_name" in p
            assert "provider" in p

    def test_create_debate_empty_question(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json={"question": "", "models": ["model-a"]})
        assert resp.status_code == 422

    def test_create_debate_missing_models(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json={"question": "Test?"})
        assert resp.status_code == 422

    def test_create_debate_empty_models(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json={"question": "Test?", "models": []})
        assert resp.status_code == 422


class TestDebateConfiguration:
    """Debate configuration and provider selection tests."""

    def test_create_with_default_provider(self, client: TestClient) -> None:
        """Provider is derived from model config when not overridden."""
        resp = client.post(
            "/api/v1/debates",
            json={"question": "Test?", "models": ["model-a"]},
        )
        assert resp.status_code == 201
        p = resp.json()["participants"][0]
        # "model-a" maps to provider_key "model_a" in config
        assert p["provider"] == "model_a"

    def test_create_with_provider_override_falls_back(self, client: TestClient) -> None:
        """Provider from request is used only for models not in config."""
        resp = client.post(
            "/api/v1/debates",
            json={
                "question": "Test?",
                "models": ["model-a"],
                "provider": "openai",
            },
        )
        assert resp.status_code == 201
        p = resp.json()["participants"][0]
        # Config model "model-a" has provider_key "model_a", so config wins
        assert p["provider"] == "model_a"

    def test_create_with_config_dict(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/debates",
            json={
                "question": "Test?",
                "models": ["model-a"],
                "config": {"rounds": 3, "strategy": "round-robin"},
            },
        )
        assert resp.status_code == 201


class TestGetDebate:
    """Debate retrieval test suite."""

    VALID_PAYLOAD = {
        "question": "Should AI be regulated?",
        "models": ["model-a", "model-b"],
    }

    def _create_debate(self, client: TestClient) -> str:
        return client.post("/api/v1/debates", json=self.VALID_PAYLOAD).json()["debate_id"]

    def test_get_debate_returns_200(self, client: TestClient) -> None:
        debate_id = self._create_debate(client)
        resp = client.get(f"/api/v1/debates/{debate_id}")
        assert resp.status_code == 200

    def test_get_debate_returns_question(self, client: TestClient) -> None:
        debate_id = self._create_debate(client)
        resp = client.get(f"/api/v1/debates/{debate_id}")
        assert resp.json()["question"] == self.VALID_PAYLOAD["question"]

    def test_get_debate_returns_participants(self, client: TestClient) -> None:
        debate_id = self._create_debate(client)
        resp = client.get(f"/api/v1/debates/{debate_id}")
        assert len(resp.json()["participants"]) == 2

    def test_get_debate_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_get_debate_invalid_id(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates/not-a-uuid")
        assert resp.status_code == 400
