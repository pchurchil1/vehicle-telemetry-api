"""add phase 2 auth signals ingestion

Revision ID: 6a9c0c8ef2e4
Revises: 1b8f4dbeca2d
Create Date: 2026-05-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a9c0c8ef2e4"
down_revision: Union[str, Sequence[str], None] = "1b8f4dbeca2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("ecu_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("data_type", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["ecu_id"], ["ecus.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vehicle_id", "name", name="uq_signal_vehicle_name"),
    )
    op.create_index(op.f("ix_signals_ecu_id"), "signals", ["ecu_id"], unique=False)
    op.create_index(op.f("ix_signals_vehicle_id"), "signals", ["vehicle_id"], unique=False)

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("accepted_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_jobs_status"), "ingestion_jobs", ["status"], unique=False)

    op.add_column("events", sa.Column("signal_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_events_signal_id"), "events", ["signal_id"], unique=False)
    op.create_foreign_key(
        "fk_events_signal_id_signals",
        "events",
        "signals",
        ["signal_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_events_signal_id_signals", "events", type_="foreignkey")
    op.drop_index(op.f("ix_events_signal_id"), table_name="events")
    op.drop_column("events", "signal_id")

    op.drop_index(op.f("ix_ingestion_jobs_status"), table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")

    op.drop_index(op.f("ix_signals_vehicle_id"), table_name="signals")
    op.drop_index(op.f("ix_signals_ecu_id"), table_name="signals")
    op.drop_table("signals")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
