"""Participant schemas — request/response models for debate participants."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParticipantResponse(BaseModel):
    """Response schema for a debate participant."""

    id: str
    debate_id: str
    model_name: str
    provider: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
