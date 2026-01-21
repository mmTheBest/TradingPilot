"""Add snapshot indexes

Revision ID: 0009_snapshot_indexes
Revises: 0008_trade_overrides
Create Date: 2026-01-21
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0009_snapshot_indexes"
down_revision = "0008_trade_overrides"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_positions_snapshot_full_tenant_book_asof",
        "positions_snapshot_full",
        ["tenant_id", "book_id", "as_of_ts"],
        unique=True,
    )
    op.create_index(
        "ix_limits_snapshot_full_tenant_book_asof",
        "limits_snapshot_full",
        ["tenant_id", "book_id", "as_of_ts"],
        unique=True,
    )
    op.create_index(
        "ix_positions_delta_tenant_book_event",
        "positions_delta",
        ["tenant_id", "book_id", "event_ts"],
    )


def downgrade() -> None:
    op.drop_index("ix_positions_delta_tenant_book_event", table_name="positions_delta")
    op.drop_index("ix_limits_snapshot_full_tenant_book_asof", table_name="limits_snapshot_full")
    op.drop_index("ix_positions_snapshot_full_tenant_book_asof", table_name="positions_snapshot_full")
