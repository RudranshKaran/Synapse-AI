"""Add response_relationships table — tracks critique-to-opinion links.

Revision ID: 002
Revises: 001
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the response_relationships table."""
    op.create_table(
        "response_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_response_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("responses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_response_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("responses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_response_relationships_source", "response_relationships", ["source_response_id"])
    op.create_index("ix_response_relationships_target", "response_relationships", ["target_response_id"])
    op.create_index("ix_response_relationships_type", "response_relationships", ["relationship_type"])


def downgrade() -> None:
    """Drop the response_relationships table."""
    op.drop_table("response_relationships")
