"""add ingestion job payload

Revision ID: f3e1c8a9d4b7
Revises: 6a9c0c8ef2e4
Create Date: 2026-06-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f3e1c8a9d4b7"
down_revision: Union[str, Sequence[str], None] = "6a9c0c8ef2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ingestion_jobs",
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.alter_column("ingestion_jobs", "payload", server_default=None)


def downgrade() -> None:
    op.drop_column("ingestion_jobs", "payload")
