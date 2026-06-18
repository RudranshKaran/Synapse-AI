"""SQLAlchemy ORM models.

All models inherit from Base and are imported here
so Alembic can discover them automatically.
"""

from app.database.models.base import Base
from app.database.models.debate import Debate
from app.database.models.participant import Participant
from app.database.models.debate_round import DebateRound
from app.database.models.response import Response
from app.database.models.consensus_report import ConsensusReport
from app.database.models.consensus_item import ConsensusItem
from app.database.models.evaluation_metric import EvaluationMetric
from app.database.models.participant_metric import ParticipantMetric
from app.database.models.response_relationship import ResponseRelationship

__all__ = [
    "Base",
    "Debate",
    "Participant",
    "DebateRound",
    "Response",
    "ConsensusReport",
    "ConsensusItem",
    "EvaluationMetric",
    "ParticipantMetric",
    "ResponseRelationship",
]
