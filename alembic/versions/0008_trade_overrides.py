"""Add trade overrides table

Revision ID: 0008_trade_overrides
Revises: 0006_market_news_item
Create Date: 2026-01-21
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0008_trade_overrides"
down_revision = "0006_market_news_item"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trade_overrides",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("book_id", sa.String(36), nullable=False),
        sa.Column("trade_id", sa.String(36), nullable=False),
        sa.Column("reason", sa.String(512), nullable=False),
        sa.Column("created_at", sa.String(32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("trade_overrides")
