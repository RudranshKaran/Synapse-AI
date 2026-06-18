"""Add participant_metrics table for per-participant evaluation data.

Revision ID: 004
Revises: 003
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "participant_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
    )
    op.create_index("ix_participant_metrics_debate_id", "participant_metrics", ["debate_id"])
    op.create_index("ix_participant_metrics_participant_id", "participant_metrics", ["participant_id"])
    op.create_index("ix_participant_metrics_name", "participant_metrics", ["metric_name"])


def downgrade() -> None:
    op.drop_table("participant_metrics")
