"""Metrics schemas — request/response models for evaluation metrics endpoints."""

from pydantic import BaseModel, Field


class MetricEntry(BaseModel):
    """A single metric entry (debate-level or participant-level)."""

    metric_name: str
    metric_value: float


class ParticipantMetricEntry(BaseModel):
    """A participant-level metric with participant identification."""

    participant_id: str
    model_name: str
    metric_name: str
    metric_value: float


class MetricsResponse(BaseModel):
    """Response schema for GET /debates/{debate_id}/metrics."""

    debate_id: str
    agreement_score: float | None = None
    opinion_drifts: dict[str, float] = Field(default_factory=dict)
    confidence_shifts: dict[str, float] = Field(default_factory=dict)
