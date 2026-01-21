"""Ingest ops tables and snapshot extensions

Revision ID: 0002_ingest_ops
Revises: 0001_initial
Create Date: 2026-01-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_ingest_ops"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def table_exists(name: str) -> bool:
        return name in inspector.get_table_names()

    def column_exists(table: str, column: str) -> bool:
        return column in [col["name"] for col in inspector.get_columns(table)]

    def unique_exists(table: str, name: str) -> bool:
        return name in {uc["name"] for uc in inspector.get_unique_constraints(table)}

    if not table_exists("ingest_run"):
        op.create_table(
            "ingest_run",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), nullable=False),
            sa.Column("book_id", sa.String(36), nullable=False),
            sa.Column("data_type", sa.String(32), nullable=False),
            sa.Column("started_at", sa.String(32), nullable=False),
            sa.Column("finished_at", sa.String(32), nullable=True),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("as_of_ts", sa.String(32), nullable=True),
            sa.Column("payload_hash", sa.String(64), nullable=True),
            sa.Column("row_count", sa.Integer, nullable=True),
            sa.Column("error", sa.String(256), nullable=True),
        )

    if not table_exists("ingest_refresh_queue"):
        op.create_table(
            "ingest_refresh_queue",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), nullable=False),
            sa.Column("book_id", sa.String(36), nullable=False),
            sa.Column("data_type", sa.String(16), nullable=False),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
            sa.Column("next_attempt_at", sa.String(32), nullable=False),
            sa.Column("last_error", sa.String(256), nullable=True),
            sa.Column("dedupe_key", sa.String(128), nullable=False),
            sa.Column("reason", sa.String(64), nullable=False),
            sa.Column("created_at", sa.String(32), nullable=False),
            sa.Column("updated_at", sa.String(32), nullable=False),
        )

    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")

    if table_exists("positions_snapshot_full") and not column_exists("positions_snapshot_full", "snapshot_json"):
        op.add_column("positions_snapshot_full", sa.Column("snapshot_json", json_type, nullable=False))
    if table_exists("positions_snapshot_full") and not column_exists("positions_snapshot_full", "payload_hash"):
        op.add_column("positions_snapshot_full", sa.Column("payload_hash", sa.String(64), nullable=False))
    if table_exists("positions_delta") and not column_exists("positions_delta", "ops_json"):
        op.add_column("positions_delta", sa.Column("ops_json", json_type, nullable=False))
    if table_exists("positions_delta") and not column_exists("positions_delta", "payload_hash"):
        op.add_column("positions_delta", sa.Column("payload_hash", sa.String(64), nullable=False))
    if table_exists("positions_delta") and not column_exists("positions_delta", "op_count"):
        op.add_column("positions_delta", sa.Column("op_count", sa.Integer, nullable=False))

    if table_exists("limits_snapshot_full") and not column_exists("limits_snapshot_full", "version_id"):
        op.add_column("limits_snapshot_full", sa.Column("version_id", sa.String(36), nullable=False))
    if table_exists("limits_snapshot_full") and not column_exists("limits_snapshot_full", "payload_hash"):
        op.add_column("limits_snapshot_full", sa.Column("payload_hash", sa.String(64), nullable=False))
    if table_exists("limits_delta") and not column_exists("limits_delta", "summary_json"):
        op.add_column("limits_delta", sa.Column("summary_json", json_type, nullable=True))

    if table_exists("risk_limits_versioned") and not column_exists("risk_limits_versioned", "id"):
        op.add_column("risk_limits_versioned", sa.Column("id", sa.String(36), nullable=True))
        if bind.dialect.name == "postgresql":
            op.execute(
                "update risk_limits_versioned set id = md5(random()::text || clock_timestamp()::text) where id is null"
            )
        op.alter_column("risk_limits_versioned", "id", nullable=False)
        if bind.dialect.name == "postgresql":
            op.drop_constraint("risk_limits_versioned_pkey", "risk_limits_versioned", type_="primary")
            op.create_primary_key("risk_limits_versioned_pkey", "risk_limits_versioned", ["id"])
    if table_exists("risk_limits_versioned") and not unique_exists("risk_limits_versioned", "uq_limits_version_row"):
        op.create_unique_constraint(
            "uq_limits_version_row",
            "risk_limits_versioned",
            ["tenant_id", "book_id", "version_id", "dimension", "dimension_id", "effective_from"],
        )


def downgrade() -> None:
    op.drop_constraint("uq_limits_version_row", "risk_limits_versioned", type_="unique")
    op.drop_constraint("risk_limits_versioned_pkey", "risk_limits_versioned", type_="primary")
    op.create_primary_key("risk_limits_versioned_pkey", "risk_limits_versioned", ["version_id"])
    op.drop_column("risk_limits_versioned", "id")

    op.drop_column("limits_delta", "summary_json")
    op.drop_column("limits_snapshot_full", "payload_hash")
    op.drop_column("limits_snapshot_full", "version_id")

    op.drop_column("positions_delta", "op_count")
    op.drop_column("positions_delta", "payload_hash")
    op.drop_column("positions_delta", "ops_json")
    op.drop_column("positions_snapshot_full", "payload_hash")
    op.drop_column("positions_snapshot_full", "snapshot_json")

    op.drop_table("ingest_refresh_queue")
    op.drop_table("ingest_run")
