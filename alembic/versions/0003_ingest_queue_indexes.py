"""Add ingest queue indexes

Revision ID: 0003_ingest_queue_indexes
Revises: 0002_ingest_ops
Create Date: 2026-01-21
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003_ingest_queue_indexes"
down_revision = "0002_ingest_ops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_ingest_refresh_queue_dedupe",
        "ingest_refresh_queue",
        ["dedupe_key"],
    )
    op.create_index("ix_ingest_refresh_queue_status", "ingest_refresh_queue", ["status"])
    op.create_index("ix_ingest_refresh_queue_next_attempt", "ingest_refresh_queue", ["next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_ingest_refresh_queue_next_attempt", table_name="ingest_refresh_queue")
    op.drop_index("ix_ingest_refresh_queue_status", table_name="ingest_refresh_queue")
    op.drop_constraint("uq_ingest_refresh_queue_dedupe", "ingest_refresh_queue", type_="unique")
