"""convert event payload to jsonb

Revision ID: 1b8f4dbeca2d
Revises: a207c1b7252d
Create Date: 2026-05-26 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "1b8f4dbeca2d"
down_revision: Union[str, Sequence[str], None] = "a207c1b7252d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "events",
        "payload",
        existing_type=sa.String(length=2000),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=False,
        postgresql_using="jsonb_build_object('raw', payload)",
    )


def downgrade() -> None:
    op.alter_column(
        "events",
        "payload",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.String(length=2000),
        existing_nullable=False,
        postgresql_using="payload::text",
    )
