"""Add API keys table

Revision ID: 0005_auth_api_keys
Revises: 0004_fx_snapshot_group
Create Date: 2026-01-21
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_auth_api_keys"
down_revision = "0004_fx_snapshot_group"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("owner", sa.String(128), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("revoked_at", sa.String(32), nullable=True),
        sa.Column("last_used_at", sa.String(32), nullable=True),
        sa.Column("created_at", sa.String(32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("api_keys")
