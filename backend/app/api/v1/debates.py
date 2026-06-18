"""Debate management endpoints.

Implements the debate lifecycle API as defined in docs/api_specification.md.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_debate_service,
    get_execution_service,
    get_metrics_service,
    get_transcript_service,
)
from app.schemas.debate import DebateCreate, DebateListParams, DebateListResponse, DebateResponse
from app.schemas.execution import DebateRunRequest, DebateRunResponse
from app.schemas.metrics import MetricsResponse
from app.schemas.transcript import Transcript
from app.services.debate_service import DebateService
from app.services.execution_service import ExecutionService
from app.services.metrics_service import MetricsService
from app.services.transcript_service import TranscriptService

router = APIRouter()


@router.post("", response_model=DebateResponse, status_code=201)
async def create_debate(
    payload: DebateCreate,
    service: DebateService = Depends(get_debate_service),
) -> DebateResponse:
    """Create a new debate session.

    Validates the request, creates the debate and participant records,
    and returns the created debate metadata.
    """
    return service.create_debate(payload)


@router.get("", response_model=DebateListResponse)
async def list_debates(
    params: DebateListParams = Depends(),
    service: DebateService = Depends(get_debate_service),
) -> DebateListResponse:
    """List debates with pagination, filtering, and search.

    Returns a frontend-friendly summary of debates ordered by
    creation date (newest first). Supports filtering by status
    and searching by question text.
    """
    return service.list_debates(params)


@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(
    debate_id: str,
    service: DebateService = Depends(get_debate_service),
) -> DebateResponse:
    """Retrieve debate details by ID.

    Returns the debate metadata including status, question,
    participants, and timestamps.
    """
    return service.get_debate(debate_id)


@router.post("/{debate_id}/run", response_model=DebateRunResponse)
async def run_debate(
    debate_id: str,
    payload: DebateRunRequest,
    service: ExecutionService = Depends(get_execution_service),
) -> DebateRunResponse:
    """Execute the full debate pipeline.

    Runs opinion generation and critique phases sequentially:
    1. Generates initial opinions from all participant models.
    2. Generates critiques from each participant targeting another's opinion.
    3. Persists all artifacts and returns results.
    """
    return service.run_debate(debate_id, payload)


@router.get("/{debate_id}/transcript", response_model=Transcript)
async def get_debate_transcript(
    debate_id: str,
    service: TranscriptService = Depends(get_transcript_service),
) -> Transcript:
    """Retrieve the complete debate transcript.

    Returns all debate artifacts including participants, rounds,
    responses, relationships, consensus, and evaluation metrics
    in a single response designed for frontend consumption.
    """
    return service.get_transcript(debate_id)


@router.get("/{debate_id}/metrics", response_model=MetricsResponse)
async def get_debate_metrics(
    debate_id: str,
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsResponse:
    """Retrieve all computed evaluation metrics for a debate.

    Returns agreement score, opinion drifts, and confidence shifts
    for each participant in the debate.
    """
    return service.get_metrics(debate_id)
