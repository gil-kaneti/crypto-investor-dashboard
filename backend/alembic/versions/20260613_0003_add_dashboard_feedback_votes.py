"""add dashboard feedback votes

Revision ID: 20260613_0003
Revises: 20260612_0002
Create Date: 2026-06-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260613_0003"
down_revision: str | None = "20260612_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "feedback",
        sa.Column("section_id", sa.String(length=80), server_default="general", nullable=False),
    )
    op.add_column("feedback", sa.Column("content_id", sa.String(length=255), nullable=True))
    op.add_column(
        "feedback",
        sa.Column("vote", sa.String(length=20), server_default="thumbs_up", nullable=False),
    )
    op.add_column("feedback", sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_index("ix_feedback_section_id", "feedback", ["section_id"], unique=False)
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"], unique=False)
    op.alter_column("feedback", "section_id", server_default=None)
    op.alter_column("feedback", "vote", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_feedback_user_id", table_name="feedback")
    op.drop_index("ix_feedback_section_id", table_name="feedback")
    op.drop_column("feedback", "metadata")
    op.drop_column("feedback", "vote")
    op.drop_column("feedback", "content_id")
    op.drop_column("feedback", "section_id")
