"""EvaluationMetric schemas — request/response models for evaluation metrics."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvaluationMetricResponse(BaseModel):
    """Response schema for an evaluation metric."""

    id: str
    debate_id: str
    metric_name: str
    metric_value: float
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
