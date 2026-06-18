"""Initial schema — create all MVP tables.

Revision ID: 001
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all MVP tables for Synapse AI."""
    
    # --- debates ---
    op.create_table(
        "debates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="created"),
        sa.Column("total_rounds", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_debates_status", "debates", ["status"])

    # --- participants ---
    op.create_table(
        "participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False, server_default="mock"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_participants_debate_id", "participants", ["debate_id"])

    # --- debate_rounds ---
    op.create_table(
        "debate_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_debate_rounds_debate_id", "debate_rounds", ["debate_id"])

    # --- responses ---
    op.create_table(
        "responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debate_rounds.id", ondelete="SET NULL"), nullable=True),
        sa.Column("participant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("response_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_responses_debate_id", "responses", ["debate_id"])
    op.create_index("ix_responses_round_id", "responses", ["round_id"])
    op.create_index("ix_responses_participant_id", "responses", ["participant_id"])
    op.create_index("ix_responses_response_type", "responses", ["response_type"])

    # --- consensus_reports ---
    op.create_table(
        "consensus_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("consensus_score", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_consensus_reports_debate_id", "consensus_reports", ["debate_id"])

    # --- evaluation_metrics ---
    op.create_table(
        "evaluation_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("debate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evaluation_metrics_debate_id", "evaluation_metrics", ["debate_id"])
    op.create_index("ix_evaluation_metrics_metric_name", "evaluation_metrics", ["metric_name"])


def downgrade() -> None:
    """Drop all MVP tables."""
    op.drop_table("evaluation_metrics")
    op.drop_table("consensus_reports")
    op.drop_table("responses")
    op.drop_table("debate_rounds")
    op.drop_table("participants")
    op.drop_table("debates")
