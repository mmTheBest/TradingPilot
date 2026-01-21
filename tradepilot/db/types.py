import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

JSONB_COMPAT = sa.JSON().with_variant(JSONB(), "postgresql")
