"""Integration tests for the production agent model architecture.

Tests that agent models (agent-a, agent-b, agent-c) work correctly
through the full debate pipeline when providers return mock responses
(simulating real API calls without keys).
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import requests

from app.providers.base import BaseModelProvider, ModelResponse
from app.core.config import settings


AGENT_CREATE_PAYLOAD = {
    "question": "Should AI-assisted code review replace human code review?",
    "models": ["agent-a", "agent-b", "agent-c"],
}
RUN_PAYLOAD = {"rounds": 1}


def _make_mock_response(content: str) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return resp


def _make_mock_gemini_response(content: str) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": content}]}}
        ]
    }
    return resp


def create_debate(client: TestClient, payload: dict | None = None) -> str:
    resp = client.post("/api/v1/debates", json=payload or AGENT_CREATE_PAYLOAD)
    return resp.json()["debate_id"]


class TestAgentDebateCreation:
    """Agent models can be used to create debates."""

    def test_create_with_agent_models_returns_201(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=AGENT_CREATE_PAYLOAD)
        assert resp.status_code == 201

    def test_create_with_agent_models_has_three_participants(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=AGENT_CREATE_PAYLOAD)
        data = resp.json()
        assert len(data["participants"]) == 3

    def test_create_with_agent_models_assigns_correct_providers(self, client: TestClient) -> None:
        resp = client.post("/api/v1/debates", json=AGENT_CREATE_PAYLOAD)
        data = resp.json()
        providers = {p["model_name"]: p["provider"] for p in data["participants"]}
        assert providers["agent-a"] == "gemini"
        assert providers["agent-b"] == "groq"
        assert providers["agent-c"] == "openrouter"


class TestAgentDebateExecution:
    """Agent models execute through the full pipeline when call_with_retry is patched."""

    MOCK_GEMINI = _make_mock_gemini_response(
        "A balanced analysis of code review practices.\nConfidence: 85"
    )
    MOCK_GROQ = _make_mock_response(
        "A critical review highlighting potential issues.\nConfidence: 72"
    )
    MOCK_OPENROUTER = _make_mock_response(
        "A devil's advocate perspective on the topic.\nConfidence: 78"
    )

    @classmethod
    def _patch_call_with_retry(cls):
        """Patch BaseModelProvider.call_with_retry to return different
        mock responses based on which provider subclass is calling.

        This is a single patch that replaces the method on the base class,
        which all providers inherit. We use side_effect to cycle through
        predefined responses, covering all phases of the debate pipeline.
        """
        responses = [
            # Phase 1: Opinion generation (3 calls: gemini, groq, openrouter)
            cls.MOCK_GEMINI,
            cls.MOCK_GROQ,
            cls.MOCK_OPENROUTER,
            # Phase 2: Critique (3 calls)
            cls.MOCK_GEMINI,
            cls.MOCK_GROQ,
            cls.MOCK_OPENROUTER,
            # Phase 3: Revision (3 calls)
            cls.MOCK_GEMINI,
            cls.MOCK_GROQ,
            cls.MOCK_OPENROUTER,
            # Phase 4: Consensus (1 call via Gemini)
            _make_mock_gemini_response(
                "Consensus Score: 70\n\n"
                "Agreements:\n- Both value code review\n"
                "- Both acknowledge AI can help\n\n"
                "Disagreements:\n- Extent of human involvement\n\n"
                "Summary:\nModerate agreement on AI-assisted review."
            ),
        ]
        return patch.object(
            BaseModelProvider,
            "call_with_retry",
            side_effect=responses,
        )

    def _run_with_patches(self, client: TestClient) -> tuple:
        """Run a debate with all provider calls mocked."""
        debate_id = create_debate(client)

        # Set dummy API keys so the providers don't raise
        settings.GEMINI_API_KEY = "test-key"
        settings.GROQ_API_KEY = "test-key"
        settings.OPENROUTER_API_KEY = "test-key"

        patch_cwr = self._patch_call_with_retry()
        try:
            patch_cwr.start()
            resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        finally:
            patch_cwr.stop()
            settings.GEMINI_API_KEY = ""
            settings.GROQ_API_KEY = ""
            settings.OPENROUTER_API_KEY = ""

        return resp, debate_id

    def test_run_with_mocked_providers_returns_200(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        assert resp.status_code == 200

    def test_run_with_mocked_providers_returns_evaluation_complete(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        assert resp.json()["status"] == "evaluation_complete"

    def test_run_with_mocked_providers_returns_three_opinions(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        assert len(resp.json()["opinions"]) == 3

    def test_run_with_mocked_providers_returns_three_critiques(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        assert len(resp.json()["critiques"]) == 3

    def test_run_with_mocked_providers_returns_three_revisions(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        assert len(resp.json()["revisions"]) == 3

    def test_run_with_mocked_providers_returns_consensus(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        consensus = resp.json()["consensus"]
        assert consensus is not None
        assert consensus["consensus_score"] == 70.0

    def test_run_with_mocked_providers_returns_evaluation(self, client: TestClient) -> None:
        resp, _ = self._run_with_patches(client)
        eval_data = resp.json()["evaluation"]
        assert eval_data is not None
        assert "agreement_score" in eval_data
        assert "opinion_drifts" in eval_data
        assert "confidence_shifts" in eval_data

    def test_run_with_mocked_providers_persists_responses(self, client: TestClient, db_session: Session) -> None:
        _, debate_id = self._run_with_patches(client)

        from app.database.models.response import Response as ResponseModel
        uuid_id = uuid.UUID(debate_id)
        responses = (
            db_session.query(ResponseModel)
            .filter(ResponseModel.debate_id == uuid_id)
            .all()
        )
        # 3 opinions + 3 critiques + 3 revisions = 9
        assert len(responses) == 9

    def test_run_mixed_agents_and_mocks(self, client: TestClient) -> None:
        """Agent + mock model mix should work with appropriate patches."""
        mixed_payload = {
            "question": "Test mixed debate?",
            "models": ["agent-a", "model-a"],
        }
        resp = client.post("/api/v1/debates", json=mixed_payload)
        assert resp.status_code == 201
        debate_id = resp.json()["debate_id"]

        # Patch call_with_retry for Gemini (agent-a) — model-a is a mock
        # The Gemini provider gets called for opinion, critique, revision, and consensus
        patch_cwr = patch.object(
            BaseModelProvider,
            "call_with_retry",
            return_value=_make_mock_gemini_response(
                "Test analysis.\nConfidence: 85"
            ),
        )
        settings.GEMINI_API_KEY = "test-key"
        try:
            patch_cwr.start()
            resp = client.post(f"/api/v1/debates/{debate_id}/run", json=RUN_PAYLOAD)
        finally:
            patch_cwr.stop()
            settings.GEMINI_API_KEY = ""

        assert resp.status_code == 200
        assert len(resp.json()["opinions"]) == 2
