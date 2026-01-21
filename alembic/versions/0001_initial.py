"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")

    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("portfolio_id", sa.String(36), nullable=True),
        sa.Column("desk_id", sa.String(36), nullable=True),
        sa.Column("base_currency", sa.String(3), nullable=False),
    )
    op.create_table(
        "issuer_master",
        sa.Column("issuer_id", sa.String(36), primary_key=True),
        sa.Column("legal_name", sa.String(255), nullable=False),
    )
    op.create_table(
        "sector_taxonomy",
        sa.Column("taxonomy_id", sa.String(36), primary_key=True),
        sa.Column("taxonomy_version", sa.String(64), nullable=False),
        sa.Column("vendor", sa.String(64), nullable=False),
        sa.Column("effective_from", sa.String(32), nullable=False),
    )
    op.create_table(
        "security_master",
        sa.Column("symbol", sa.String(32), primary_key=True),
        sa.Column("issuer_id", sa.String(36), nullable=False),
        sa.Column("sector_id", sa.String(36), nullable=False),
        sa.Column("taxonomy_id", sa.String(36), nullable=False),
        sa.Column("updated_at", sa.String(32), nullable=False),
    )
    op.create_table(
        "fx_rate_snapshot",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("vendor", sa.String(64), nullable=False),
        sa.Column("as_of_ts", sa.String(32), nullable=False),
        sa.Column("base_ccy", sa.String(3), nullable=False),
        sa.Column("quote_ccy", sa.String(3), nullable=False),
        sa.Column("mid_rate", sa.Float, nullable=False),
    )
    op.create_table(
        "positions_snapshot_full",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("as_of_ts", sa.String(32), nullable=False),
        sa.Column("net_exposure", sa.Float, nullable=False),
        sa.Column("gross_notional", sa.Float, nullable=False),
        sa.Column("snapshot_json", json_type, nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
    )
    op.create_table(
        "positions_delta",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("event_ts", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("ops_json", json_type, nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("op_count", sa.Integer, nullable=False),
    )
    op.create_table(
        "risk_limits_versioned",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("dimension", sa.String(32), nullable=False),
        sa.Column("dimension_id", sa.String(36), nullable=False),
        sa.Column("absolute_limit", sa.Float, nullable=False),
        sa.Column("relative_limit_pct", sa.Float, nullable=False),
        sa.Column("effective_from", sa.String(32), nullable=False),
        sa.Column("effective_to", sa.String(32), nullable=True),
        sa.UniqueConstraint(
            "tenant_id",
            "book_id",
            "version_id",
            "dimension",
            "dimension_id",
            "effective_from",
            name="uq_limits_version_row",
        ),
    )
    op.create_table(
        "limits_snapshot_full",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("as_of_ts", sa.String(32), nullable=False),
        sa.Column("version_id", sa.String(36), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
    )
    op.create_table(
        "limits_delta",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("version_id", sa.String(36), nullable=False),
        sa.Column("event_ts", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("summary_json", json_type, nullable=True),
    )
    op.create_table(
        "audit_event",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("as_of_ts", sa.String(32), nullable=False),
    )
    op.create_table(
        "staged_trades",
        sa.Column("trade_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("order_type", sa.String(16), nullable=False),
        sa.Column("limit_price", sa.Float, nullable=True),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("emsx_order_id", sa.String(64), nullable=True),
        sa.Column("positions_as_of_ts", sa.String(32), nullable=False),
        sa.Column("limits_version_id", sa.String(36), nullable=False),
        sa.Column("fx_rate_snapshot_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.String(32), nullable=False),
    )
    op.create_table(
        "trade_approvals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trade_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(512), nullable=True),
        sa.Column("slack_user_id", sa.String(64), nullable=False),
        sa.Column("approver_id", sa.String(36), nullable=True),
        sa.Column("approver_effective_from", sa.String(32), nullable=True),
        sa.Column("approver_effective_to", sa.String(32), nullable=True),
        sa.Column("created_at", sa.String(32), nullable=False),
    )
    op.create_table(
        "trade_submit_queue",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trade_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False),
        sa.Column("next_attempt_at", sa.String(32), nullable=False),
        sa.Column("last_error", sa.String(512), nullable=True),
        sa.Column("created_at", sa.String(32), nullable=False),
        sa.Column("updated_at", sa.String(32), nullable=False),
    )
    op.create_table(
        "slack_approvers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("slack_user_id", sa.String(64), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("effective_from", sa.String(32), nullable=False),
        sa.Column("effective_to", sa.String(32), nullable=True),
        sa.Column("added_by", sa.String(64), nullable=False),
        sa.Column("added_at", sa.String(32), nullable=False),
    )
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
        sa.UniqueConstraint("dedupe_key", name="uq_ingest_refresh_queue_dedupe"),
    )
    op.create_index("ix_ingest_refresh_queue_status", "ingest_refresh_queue", ["status"])
    op.create_index("ix_ingest_refresh_queue_next_attempt", "ingest_refresh_queue", ["next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_ingest_refresh_queue_next_attempt", table_name="ingest_refresh_queue")
    op.drop_index("ix_ingest_refresh_queue_status", table_name="ingest_refresh_queue")
    op.drop_table("ingest_refresh_queue")
    op.drop_table("ingest_run")
    op.drop_table("slack_approvers")
    op.drop_table("trade_submit_queue")
    op.drop_table("trade_approvals")
    op.drop_table("staged_trades")
    op.drop_table("audit_event")
    op.drop_table("limits_delta")
    op.drop_table("limits_snapshot_full")
    op.drop_table("risk_limits_versioned")
    op.drop_table("positions_delta")
    op.drop_table("positions_snapshot_full")
    op.drop_table("fx_rate_snapshot")
    op.drop_table("security_master")
    op.drop_table("sector_taxonomy")
    op.drop_table("issuer_master")
    op.drop_table("books")
    op.drop_table("tenants")
