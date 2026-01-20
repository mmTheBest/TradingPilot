# TradePilot Data Layer Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate the new data-layer modules with the existing trade workflow so staging uses freshness gating, limit evaluation, and returns audit context fields.

**Architecture:** Introduce a data provider interface that supplies snapshot metadata (as-of timestamps, limits version, FX snapshot) plus exposures. Update TradeService to use FreshnessGate and limit evaluation, then wire the trade API to use the provider and surface context fields in responses.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, Alembic, pytest.

**Reference Docs:** `docs/plans/2026-01-19-tradepilot-data-layer-plan.md`

**Skill Reminder:** Use @superpowers:test-driven-development for each task.

### Task 1: Extend trade models with tenancy + context fields

**Files:**
- Modify: `tradepilot/trades/models.py`
- Modify: `tests/test_trade_models.py`

**Step 1: Write the failing test**

```python
import pytest

from tradepilot.trades.models import TradeRequest


def test_trade_request_requires_book_id():
    with pytest.raises(ValueError):
        TradeRequest(symbol="AAPL", side="buy", quantity=10, tenant_id="t-1")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_trade_models.py -v`  
Expected: FAIL because `book_id` is not enforced yet.

**Step 3: Write minimal implementation**

```python
class TradeRequest(BaseModel):
    tenant_id: str
    book_id: str
    symbol: str
    side: TradeSide
    quantity: float = Field(gt=0)
    order_type: str = "market"
    limit_price: Optional[float] = None


class StagedTrade(BaseModel):
    trade_id: str
    request: TradeRequest
    risk_checks: list[RiskCheckResult]
    positions_as_of_ts: str
    limits_version_id: str
    fx_rate_snapshot_id: str
    emsx_order_id: Optional[str] = None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_trade_models.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tradepilot/trades/models.py tests/test_trade_models.py
git commit -m "feat: add tenancy and context fields to trade models"
```

### Task 2: Add data provider interface + in-memory provider

**Files:**
- Create: `tradepilot/data/provider.py`
- Create: `tests/data/test_provider.py`

**Step 1: Write the failing test**

```python
from tradepilot.data.provider import InMemoryDataProvider


def test_inmemory_provider_returns_snapshot():
    provider = InMemoryDataProvider()
    snapshot = provider.get_snapshot(tenant_id="t-1", book_id="b-1", symbol="AAPL")
    assert snapshot.positions_as_of_ts
    assert snapshot.limits_version_id
    assert snapshot.fx_rate_snapshot_id
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_provider.py -v`  
Expected: FAIL with `ModuleNotFoundError` for `tradepilot.data.provider`.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass


@dataclass
class DataSnapshot:
    positions_as_of_ts: str
    limits_as_of_ts: str
    limits_version_id: str
    fx_rate_snapshot_id: str
    gross_notional: float
    issuer_exposure: float
    sector_exposure: float


class InMemoryDataProvider:
    def get_snapshot(self, tenant_id: str, book_id: str, symbol: str) -> DataSnapshot:
        return DataSnapshot(
            positions_as_of_ts="2026-01-19T10:00:00Z",
            limits_as_of_ts="2026-01-19T09:30:00Z",
            limits_version_id="v-1",
            fx_rate_snapshot_id="fx-1",
            gross_notional=1_000_000,
            issuer_exposure=100_000,
            sector_exposure=200_000,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/data/test_provider.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tradepilot/data/provider.py tests/data/test_provider.py
git commit -m "feat: add data provider interface"
```

### Task 3: Integrate freshness gating + limits into TradeService

**Files:**
- Modify: `tradepilot/trades/service.py`
- Modify: `tests/test_trade_service.py`

**Step 1: Write the failing test**

```python
import pytest

from tradepilot.data.provider import InMemoryDataProvider
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.service import RiskCheckFailed, TradeService


def test_trade_service_blocks_when_positions_stale():
    provider = InMemoryDataProvider()
    service = TradeService(emsx_client=FakeEmsxClient(), data_provider=provider)
    request = TradeRequest(tenant_id="t-1", book_id="b-1", symbol="AAPL", side="buy", quantity=10)
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request, positions_age_minutes=10, limits_age_minutes=10)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_trade_service.py -v`  
Expected: FAIL because `TradeService` does not use freshness gating.

**Step 3: Write minimal implementation**

```python
from dataclasses import dataclass

from tradepilot.data.provider import InMemoryDataProvider
from tradepilot.gating.freshness import FreshnessGate
from tradepilot.risk.checks import check_best_execution_prompt, check_liquidity_slippage
from tradepilot.risk.limits_eval import evaluate_limit
from tradepilot.trades.models import RiskCheckResult, StagedTrade, TradeRequest


@dataclass
class TradeService:
    emsx_client: EmsxClient
    data_provider: InMemoryDataProvider

    def stage_trade(self, request: TradeRequest, positions_age_minutes: int, limits_age_minutes: int) -> StagedTrade:
        gate = FreshnessGate(positions_sla_minutes=5, limits_sla_minutes=60)
        gate_result = gate.evaluate(positions_age_minutes, limits_age_minutes)
        if not gate_result.allowed:
            raise RiskCheckFailed("freshness gate failed")

        snapshot = self.data_provider.get_snapshot(request.tenant_id, request.book_id, request.symbol)
        checks: list[RiskCheckResult] = [
            evaluate_limit(snapshot.issuer_exposure, 100_000, 0.1, snapshot.gross_notional),
            evaluate_limit(snapshot.sector_exposure, 200_000, 0.25, snapshot.gross_notional),
            check_liquidity_slippage(1_000_000, request.quantity),
            check_best_execution_prompt(request.order_type),
        ]
        if any(check.status == "failed" for check in checks):
            raise RiskCheckFailed("risk checks failed")

        emsx_order_id = self.emsx_client.stage_order(request)
        return StagedTrade(
            trade_id=emsx_order_id,
            request=request,
            risk_checks=checks,
            positions_as_of_ts=snapshot.positions_as_of_ts,
            limits_version_id=snapshot.limits_version_id,
            fx_rate_snapshot_id=snapshot.fx_rate_snapshot_id,
            emsx_order_id=emsx_order_id,
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_trade_service.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tradepilot/trades/service.py tests/test_trade_service.py
git commit -m "feat: integrate freshness gating and limits in trade service"
```

### Task 4: Wire trade API to provider and updated trade models

**Files:**
- Modify: `tradepilot/api/trades.py`
- Modify: `tests/test_trade_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from tradepilot.main import app


def test_stage_trade_endpoint_returns_context():
    client = TestClient(app)
    response = client.post(
        "/api/v1/trades/stage",
        json={"tenant_id": "t-1", "book_id": "b-1", "symbol": "AAPL", "side": "buy", "quantity": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["positions_as_of_ts"]
    assert body["limits_version_id"]
    assert body["fx_rate_snapshot_id"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_trade_api.py -v`  
Expected: FAIL because API does not include context fields.

**Step 3: Write minimal implementation**

```python
from tradepilot.data.provider import InMemoryDataProvider

provider = InMemoryDataProvider()
service = TradeService(emsx_client=FakeEmsxClient(), data_provider=provider)


@router.post("/api/v1/trades/stage")
def stage_trade(request: TradeRequest):
    staged = service.stage_trade(request, positions_age_minutes=0, limits_age_minutes=0)
    return staged.model_dump()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_trade_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tradepilot/api/trades.py tests/test_trade_api.py
git commit -m "feat: wire trade api to data provider"
```

### Task 5: Add Alembic dependency for data layer

**Files:**
- Modify: `pyproject.toml`

**Step 1: Write the failing test**

```python
from importlib import import_module


def test_alembic_dependency_available():
    assert import_module("alembic")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_dependencies.py -v`  
Expected: FAIL with `ModuleNotFoundError` for `alembic`.

**Step 3: Write minimal implementation**

```toml
dependencies = [
  ...
  "alembic>=1.13.0",
]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_dependencies.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml tests/test_dependencies.py
git commit -m "chore: add alembic dependency"
```
