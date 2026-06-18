"""Transcript schemas — response model for the debate transcript endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field


class TranscriptParticipant(BaseModel):
    """Participant information in the transcript."""

    participant_id: str
    model_name: str
    provider: str


class TranscriptEntry(BaseModel):
    """A single model response entry in the transcript."""

    response_id: str
    participant_id: str
    model_name: str
    response_type: str
    content: str
    confidence_score: float | None = None
    created_at: datetime | None = None
    relationships: list[dict] = Field(default_factory=list)


class TranscriptRound(BaseModel):
    """A single round/phase in the debate."""

    round_id: str
    round_number: int
    phase: str
    created_at: datetime | None = None
    responses: list[TranscriptEntry] = Field(default_factory=list)


class TranscriptConsensus(BaseModel):
    """Consensus information in the transcript."""

    consensus_score: float | None = None
    agreements: list[str] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    summary: str | None = None


class TranscriptMetricsInfo(BaseModel):
    """Evaluation metrics in the transcript."""

    agreement_score: float | None = None
    opinion_drifts: dict[str, float] = Field(default_factory=dict)
    confidence_shifts: dict[str, float] = Field(default_factory=dict)


class Transcript(BaseModel):
    """Complete debate transcript response."""

    debate_id: str
    question: str
    status: str
    participants: list[TranscriptParticipant] = Field(default_factory=list)
    rounds: list[TranscriptRound] = Field(default_factory=list)
    consensus: TranscriptConsensus | None = None
    metrics: TranscriptMetricsInfo | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
