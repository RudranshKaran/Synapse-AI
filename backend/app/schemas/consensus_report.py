"""ConsensusReport schemas — request/response models for consensus reports."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConsensusReportResponse(BaseModel):
    """Response schema for a consensus report."""

    id: str
    debate_id: str
    consensus_score: float | None = None
    summary: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
