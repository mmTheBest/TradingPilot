from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from tradepilot.ingest.adapters.positions_db import PositionsDbAdapter


def test_positions_db_adapter_reads_view():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                create table positions_view (
                  tenant_id text,
                  book_id text,
                  symbol text,
                  quantity real,
                  price real,
                  currency text,
                  as_of_ts text
                )
                """
            )
        )
        conn.execute(
            text(
                "insert into positions_view values ('t1','b1','AAPL',10,100.0,'USD','2026-01-20T10:00:00Z')"
            )
        )

    adapter = PositionsDbAdapter(session_factory=SessionLocal, table_name="positions_view")
    as_of_ts, rows = adapter.fetch_positions("t1", "b1")
    assert as_of_ts == "2026-01-20T10:00:00Z"
    assert rows[0]["symbol"] == "AAPL"
