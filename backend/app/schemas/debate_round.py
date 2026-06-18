"""DebateRound schemas — request/response models for debate rounds."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DebateRoundResponse(BaseModel):
    """Response schema for a debate round."""

    id: str
    debate_id: str
    round_number: int
    phase: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
