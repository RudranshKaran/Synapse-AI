"""Add consensus_items table for agreements/disagreements.

Revision ID: 003
Revises: 002
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consensus_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("consensus_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("consensus_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
    )
    op.create_index("ix_consensus_items_report_id", "consensus_items", ["consensus_report_id"])
    op.create_index("ix_consensus_items_type", "consensus_items", ["item_type"])


def downgrade() -> None:
    op.drop_table("consensus_items")
