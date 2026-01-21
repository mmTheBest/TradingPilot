"""Add market news item table

Revision ID: 0006_market_news_item
Revises: 0005_auth_api_keys
Create Date: 2026-01-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0006_market_news_item"
down_revision = "0005_auth_api_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")
    op.create_table(
        "market_news_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("headline", sa.String(512), nullable=False),
        sa.Column("timestamp", sa.String(32), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("payload_json", json_type, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("market_news_item")
