"""Response schemas — request/response models for model-generated outputs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResponseResponse(BaseModel):
    """Response schema for a model output."""

    id: str
    debate_id: str
    round_id: str | None = None
    participant_id: str
    response_type: str
    content: str
    confidence_score: float | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
