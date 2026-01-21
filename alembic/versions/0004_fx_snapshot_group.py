"""Add FX snapshot group id

Revision ID: 0004_fx_snapshot_group
Revises: 0003_ingest_queue_indexes
Create Date: 2026-01-21
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_fx_snapshot_group"
down_revision = "0003_ingest_queue_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("fx_rate_snapshot", sa.Column("snapshot_id", sa.String(36), nullable=False))


def downgrade() -> None:
    op.drop_column("fx_rate_snapshot", "snapshot_id")
