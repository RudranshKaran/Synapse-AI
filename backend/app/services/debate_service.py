"""Debate service — business logic for debate management."""

import uuid

from fastapi import HTTPException, status

from app.repositories.debate_repository import DebateRepository
from app.schemas.debate import (
    DebateCreate,
    DebateListItem,
    DebateListParams,
    DebateListResponse,
    DebateResponse,
    ParticipantInfo,
)


class DebateService:
    """Service layer for debate operations.

    Orchestrates business logic by coordinating between
    the repository and API layers.
    """

    def __init__(self, repository: DebateRepository) -> None:
        self._repository = repository

    def list_debates(self, params: DebateListParams) -> DebateListResponse:
        """List debates with pagination, filtering, and search.

        Efficiently fetches participant counts and agreement scores
        in bulk queries to avoid N+1 issues.

        Args:
            params: Validated list parameters (page, page_size, status, search).

        Returns:
            DebateListResponse with paginated results and total count.
        """
        debates, total = self._repository.list_debates(
            page=params.page,
            page_size=params.page_size,
            status_filter=params.status,
            search=params.search,
        )

        # Bulk-fetch participant counts and agreement scores
        debate_ids = [d.id for d in debates]
        participant_counts = self._repository.get_participant_counts(debate_ids)
        agreement_scores = self._repository.get_agreement_scores(debate_ids)

        items = [
            DebateListItem(
                debate_id=str(d.id),
                question=d.question,
                status=d.status,
                created_at=d.created_at,
                completed_at=d.completed_at,
                participant_count=participant_counts.get(d.id, 0),
                agreement_score=agreement_scores.get(d.id),
            )
            for d in debates
        ]

        return DebateListResponse(
            total=total,
            page=params.page,
            page_size=params.page_size,
            debates=items,
        )

    def create_debate(self, payload: DebateCreate) -> DebateResponse:
        """Create a new debate with participants.

        Args:
            payload: Validated debate creation request.

        Returns:
            DebateResponse with the created debate metadata.

        Raises:
            HTTPException: If debate creation fails.
        """
        debate = self._repository.create_debate(
            question=payload.question, total_rounds=1
        )

        participant_infos: list[ParticipantInfo] = []
        for model_name in payload.models:
            participant = self._repository.add_participant(
                debate_id=debate.id,
                model_name=model_name,
                provider=payload.provider,
            )
            participant_infos.append(
                ParticipantInfo(
                    participant_id=str(participant.id),
                    model_name=participant.model_name,
                    provider=participant.provider,
                )
            )

        return DebateResponse(
            debate_id=str(debate.id),
            question=debate.question,
            status=debate.status,
            participants=participant_infos,
            created_at=debate.created_at,
            completed_at=debate.completed_at,
        )

    def get_debate(self, debate_id: str) -> DebateResponse:
        """Retrieve debate details by ID.

        Args:
            debate_id: The debate UUID as a string.

        Returns:
            DebateResponse with debate metadata.

        Raises:
            HTTPException: If debate is not found.
        """
        try:
            debate_uuid = uuid.UUID(debate_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid debate ID format: {debate_id}",
            )

        debate = self._repository.get_debate_by_id(debate_uuid)
        if debate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Debate not found: {debate_id}",
            )

        participants = self._repository.get_participants_for_debate(debate_uuid)
        participant_infos = [
            ParticipantInfo(
                participant_id=str(p.id),
                model_name=p.model_name,
                provider=p.provider,
            )
            for p in participants
        ]

        return DebateResponse(
            debate_id=str(debate.id),
            question=debate.question,
            status=debate.status,
            participants=participant_infos,
            created_at=debate.created_at,
            completed_at=debate.completed_at,
        )
