from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.api import trades as trades_api
from tradepilot.data.provider import DataSnapshot, InMemoryDataProvider
from tradepilot.db.base import Base
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.auth.dependencies import require_api_key
from tradepilot.main import app
from tradepilot.trades.repository import TradeRepository
from tradepilot.trades.service import TradeService


def test_trade_service_has_ingest_queue():
    service = trades_api.get_trade_service()
    assert service.ingest_queue is not None


def test_stage_trade_endpoint():
    snapshot = DataSnapshot(
        positions_age_minutes=0,
        limits_age_minutes=0,
        current_exposure=0.0,
        absolute_limit=1_000_000.0,
        relative_limit_pct=1.0,
        book_notional=10_000_000.0,
        adv=1_000_000.0,
        positions_as_of_ts="2026-01-19T09:30:00Z",
        limits_version_id="limits-1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=0.0,
        issuer_absolute_limit=10_000_000.0,
        issuer_relative_limit_pct=1.0,
        sector_exposure=0.0,
        sector_absolute_limit=10_000_000.0,
        sector_relative_limit_pct=1.0,
        fx_rate_snapshot_id="fx-1",
    )
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
        repository=TradeRepository(session_factory=SessionLocal),
    )
    app.dependency_overrides[trades_api.get_trade_service] = lambda: service
    app.dependency_overrides[require_api_key] = lambda: {"tenant_id": "tenant-1", "role": "OPS"}
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/trades/stage",
            json={
                "tenant_id": "tenant-1",
                "book_id": "book-1",
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "price": 100.0,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        UUID(payload["trade_id"])
        assert payload["emsx_order_id"].startswith("emsx-")
        assert payload["status"] == "staged"
        assert payload["positions_as_of_ts"] == "2026-01-19T09:30:00Z"
        assert payload["limits_version_id"] == "limits-1"
        assert payload["fx_rate_snapshot_id"] == "fx-1"
    finally:
        app.dependency_overrides.clear()
