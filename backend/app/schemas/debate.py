"""Debate schemas — request/response models for debate endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParticipantInfo(BaseModel):
    """Brief participant info included in debate responses."""

    participant_id: str
    model_name: str
    provider: str


class DebateCreate(BaseModel):
    """Request schema for creating a new debate."""

    question: str = Field(
        ..., min_length=1, max_length=5000, description="The debate question"
    )
    models: list[str] = Field(
        ..., min_length=1, max_length=10, description="List of model identifiers"
    )
    provider: str = Field(
        default="mock",
        description="Provider type for all models ('mock' or 'openai')",
    )
    config: dict = Field(
        default_factory=dict,
        description="Optional debate configuration (reserved for future use)",
    )


class DebateResponse(BaseModel):
    """Response schema for debate details."""

    debate_id: str = Field(..., alias="debate_id")
    question: str
    status: str
    participants: list[ParticipantInfo] = Field(default_factory=list)
    created_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DebateListItem(BaseModel):
    """Summary view of a debate for list endpoints."""

    debate_id: str
    question: str
    status: str
    created_at: datetime | None = None
    completed_at: datetime | None = None
    participant_count: int = 0
    agreement_score: float | None = None


class DebateListParams(BaseModel):
    """Query parameters for listing debates."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    status: str | None = Field(default=None, description="Filter by debate status")
    search: str | None = Field(default=None, max_length=200, description="Search in question text")


class DebateListResponse(BaseModel):
    """Paginated response for debate listing."""

    total: int
    page: int
    page_size: int
    debates: list[DebateListItem]
