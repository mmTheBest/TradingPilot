import os
from pathlib import Path

from alembic import command
from alembic.config import Config


def test_alembic_upgrade_head(tmp_path):
    db_path = tmp_path / "alembic_test.db"
    os.environ["TRADEPILOT_DATABASE_URL"] = f"sqlite:///{db_path}"
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(config, "head")
