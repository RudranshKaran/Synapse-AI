"""Tests for the debate listing endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.debate import Debate
from app.database.models.participant import Participant
from app.database.models.evaluation_metric import EvaluationMetric


BASE_PAYLOAD = {
    "question": "Should AI-generated code be deployed to production?",
    "models": ["model-a", "model-b"],
}
RUN_PAYLOAD = {"rounds": 1}


def create_debate(client: TestClient, question: str | None = None) -> str:
    payload = {**BASE_PAYLOAD}
    if question:
        payload["question"] = question
    return client.post("/api/v1/debates", json=payload).json()["debate_id"]


class TestListDebatesBasic:
    """Basic debate listing tests."""

    def test_list_returns_200(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates")
        assert resp.status_code == 200

    def test_list_returns_empty(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates")
        data = resp.json()
        assert data["total"] == 0
        assert data["debates"] == []

    def test_list_returns_one_debate(self, client: TestClient) -> None:
        create_debate(client)
        resp = client.get("/api/v1/debates")
        data = resp.json()
        assert data["total"] == 1
        assert len(data["debates"]) == 1

    def test_list_returns_multiple(self, client: TestClient) -> None:
        create_debate(client)
        create_debate(client)
        create_debate(client)
        resp = client.get("/api/v1/debates")
        data = resp.json()
        assert data["total"] == 3
        assert len(data["debates"]) == 3

    def test_list_item_has_required_fields(self, client: TestClient) -> None:
        create_debate(client)
        resp = client.get("/api/v1/debates")
        item = resp.json()["debates"][0]
        assert "debate_id" in item
        assert "question" in item
        assert "status" in item
        assert "created_at" in item
        assert "participant_count" in item
        assert "agreement_score" in item

    def test_list_returns_pagination_fields(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates")
        data = resp.json()
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "debates" in data


class TestListPagination:
    """Pagination tests."""

    def _create_n(self, client: TestClient, n: int) -> None:
        for i in range(n):
            create_debate(client, f"Question number {i}?")

    def test_page_size_default(self, client: TestClient) -> None:
        self._create_n(client, 5)
        resp = client.get("/api/v1/debates")
        assert resp.json()["page_size"] == 20

    def test_page_size_custom(self, client: TestClient) -> None:
        self._create_n(client, 5)
        resp = client.get("/api/v1/debates?page_size=2")
        assert resp.json()["page_size"] == 2
        assert len(resp.json()["debates"]) == 2

    def test_page_two(self, client: TestClient) -> None:
        self._create_n(client, 5)
        resp = client.get("/api/v1/debates?page=2&page_size=2")
        data = resp.json()
        assert data["page"] == 2
        assert len(data["debates"]) == 2  # 3rd and 4th items

    def test_last_page_partial(self, client: TestClient) -> None:
        self._create_n(client, 5)
        resp = client.get("/api/v1/debates?page=3&page_size=2")
        data = resp.json()
        assert len(data["debates"]) == 1  # 5th item only

    def test_page_beyond_total(self, client: TestClient) -> None:
        self._create_n(client, 3)
        resp = client.get("/api/v1/debates?page=10&page_size=10")
        data = resp.json()
        assert data["total"] == 3
        assert len(data["debates"]) == 0

    def test_total_remains_accurate(self, client: TestClient) -> None:
        self._create_n(client, 7)
        resp = client.get("/api/v1/debates?page=2&page_size=3")
        data = resp.json()
        assert data["total"] == 7
        assert len(data["debates"]) == 3

    def test_invalid_page_zero(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates?page=0")
        assert resp.status_code == 422

    def test_invalid_page_size_too_large(self, client: TestClient) -> None:
        resp = client.get("/api/v1/debates?page_size=200")
        assert resp.status_code == 422


class TestListOrdering:
    """Ordering tests — newest first by default."""

    def test_newest_first(self, client: TestClient, db_session: Session) -> None:
        """Debates should be ordered by created_at descending."""
        from datetime import datetime, timezone
        import uuid
        # Create debates with explicit timestamps via direct DB insertion
        for i in range(3):
            debate = Debate(
                id=uuid.uuid4(),
                question=f"Question {i}?",
                status="created",
                created_at=datetime(2026, 6, 18, 12, 0, i, tzinfo=timezone.utc),
            )
            db_session.add(debate)
        db_session.commit()
        resp = client.get("/api/v1/debates")
        debates = resp.json()["debates"]
        assert len(debates) == 3
        timestamps = [d["created_at"] for d in debates]
        assert timestamps == sorted(timestamps, reverse=True)


class TestListFilterByStatus:
    """Status filtering tests."""

    def test_filter_by_status(self, client: TestClient, db_session: Session) -> None:
        import uuid

        did1 = create_debate(client, "Running?")
        did2 = create_debate(client, "Done?")
        # Manually set status for testing
        db_session.query(Debate).filter(Debate.id == uuid.UUID(did1)).update(
            {"status": "running"}
        )
        db_session.commit()

        resp = client.get("/api/v1/debates?status=running")
        data = resp.json()
        assert data["total"] == 1
        assert data["debates"][0]["debate_id"] == did1

    def test_filter_no_match(self, client: TestClient) -> None:
        create_debate(client)
        resp = client.get("/api/v1/debates?status=nonexistent")
        data = resp.json()
        assert data["total"] == 0


class TestListSearch:
    """Search tests."""

    def test_search_matches_question(self, client: TestClient) -> None:
        create_debate(client, "Should AI be regulated?")
        create_debate(client, "Is climate change real?")
        resp = client.get("/api/v1/debates?search=climate")
        data = resp.json()
        assert data["total"] == 1
        assert "climate" in data["debates"][0]["question"].lower()

    def test_search_partial_match(self, client: TestClient) -> None:
        create_debate(client, "AI regulation in healthcare?")
        resp = client.get("/api/v1/debates?search=regul")
        assert resp.json()["total"] == 1

    def test_search_case_insensitive(self, client: TestClient) -> None:
        create_debate(client, "Should AI be regulated?")
        resp = client.get("/api/v1/debates?search=AI")
        assert resp.json()["total"] == 1

    def test_search_no_match(self, client: TestClient) -> None:
        create_debate(client, "A question about AI.")
        resp = client.get("/api/v1/debates?search=zzzzz")
        assert resp.json()["total"] == 0


class TestListParticipantCount:
    """Participant count tests."""

    def test_participant_count_two(self, client: TestClient) -> None:
        create_debate(client)
        resp = client.get("/api/v1/debates")
        assert resp.json()["debates"][0]["participant_count"] == 2

    def test_participant_count_three(self, client: TestClient) -> None:
        client.post(
            "/api/v1/debates",
            json={
                "question": "Three models?",
                "models": ["model-a", "model-b", "model-c"],
            },
        )
        resp = client.get("/api/v1/debates")
        assert resp.json()["debates"][0]["participant_count"] == 3

    def test_participant_count_zero_if_none(self, client: TestClient, db_session: Session) -> None:
        import uuid
        did = create_debate(client)
        # Remove participants
        db_session.query(Participant).filter(
            Participant.debate_id == uuid.UUID(did)
        ).delete()
        db_session.commit()
        resp = client.get("/api/v1/debates")
        assert resp.json()["debates"][0]["participant_count"] == 0


class TestListAgreementScore:
    """Agreement score inclusion tests."""

    def test_agreement_score_none_if_not_run(self, client: TestClient) -> None:
        create_debate(client)
        resp = client.get("/api/v1/debates")
        assert resp.json()["debates"][0]["agreement_score"] is None

    def test_agreement_score_present_after_run(self, client: TestClient) -> None:
        did = create_debate(client)
        client.post(f"/api/v1/debates/{did}/run", json=RUN_PAYLOAD)
        resp = client.get("/api/v1/debates")
        score = resp.json()["debates"][0]["agreement_score"]
        assert score is not None
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_agreement_score_multiple_debates(self, client: TestClient) -> None:
        did1 = create_debate(client, "First?")
        did2 = create_debate(client, "Second?")
        client.post(f"/api/v1/debates/{did1}/run", json=RUN_PAYLOAD)
        resp = client.get("/api/v1/debates")
        scores = {d["debate_id"]: d["agreement_score"] for d in resp.json()["debates"]}
        assert scores[did1] is not None
        assert scores[did2] is None


class TestListCombinedFilters:
    """Combined filtering tests."""

    def test_status_and_search(self, client: TestClient, db_session: Session) -> None:
        import uuid
        did = create_debate(client, "Unique keyword xyz123")
        db_session.query(Debate).filter(Debate.id == uuid.UUID(did)).update(
            {"status": "running"}
        )
        db_session.commit()

        resp = client.get("/api/v1/debates?status=running&search=xyz123")
        assert resp.json()["total"] == 1

    def test_status_and_search_no_match(self, client: TestClient) -> None:
        create_debate(client, "Test question.")
        resp = client.get("/api/v1/debates?status=running&search=test")
        assert resp.json()["total"] == 0
