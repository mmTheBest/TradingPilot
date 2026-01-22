# TradePilot

TradePilot is a trading-ops and risk-gating service for staging trades safely. It ingests
positions, risk limits, FX rates, and reference data, evaluates exposure and freshness,
and blocks or allows trades based on risk rules with explicit override workflows.

## What this project is for

- **Trade staging with risk checks**: validate exposure, issuer/sector limits, liquidity,
  and best-execution prompts before an order can be staged.
- **Freshness gating**: fail closed if positions/limits are stale, with on-demand refresh
  and logged override paths.
- **Ingestion pipeline**: scheduled and on-demand ingestion of positions, limits, FX, and
  reference data into Postgres with audit trails.
- **Auditability**: store snapshots, deltas, and staged-trade metadata to replay decisions.
- **Ops integrations**: chatops approvals, metrics, and operational safeguards.

## Requirements

- Python **3.12+**
- Postgres **14+**

## Installation

```bash
cd /Users/mm/Projects/agent/TradePilot
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Configuration

TradePilot reads environment variables with the `TRADEPILOT_` prefix (see
`tradepilot/config.py`). Common settings:

```bash
export TRADEPILOT_DATABASE_URL="postgresql+psycopg://tradepilot:tradepilot@localhost:5432/tradepilot"
export TRADEPILOT_INGEST_POKE_SECRET="change-me"
export TRADEPILOT_POSITIONS_VIEW="positions_view"
export TRADEPILOT_LIMITS_ADAPTER_KIND="fixture"   # or "api"
export TRADEPILOT_LIMITS_API_ENDPOINT="http://localhost:9100"
export TRADEPILOT_FX_ADAPTER_KIND="fixture"       # or "api"
export TRADEPILOT_FX_API_ENDPOINT="http://localhost:9200"
export TRADEPILOT_REFERENCE_ADAPTER_KIND="api"
export TRADEPILOT_REFERENCE_API_ENDPOINT="http://localhost:9300"
```

## Database setup

Run migrations:

```bash
export TRADEPILOT_DATABASE_URL="postgresql+psycopg://tradepilot:tradepilot@localhost:5432/tradepilot"
alembic upgrade head
```

Seed at least one book and API key so ingestion and API calls work:

```sql
-- books
INSERT INTO books (id, tenant_id, portfolio_id, desk_id, base_currency)
VALUES ('book-1', 'tenant-1', 'portfolio-1', 'desk-1', 'USD');

-- api keys
INSERT INTO api_keys (id, tenant_id, role, owner, key_hash, created_at)
VALUES ('local-ops-key', 'tenant-1', 'OPS', 'local-dev', 'n/a', '2026-01-22T00:00:00Z');
```

The API key is currently looked up by primary key (`api_keys.id`), so the `X-API-Key`
header should match the `id` value.

## Running the API

```bash
.venv/bin/uvicorn tradepilot.main:app --reload --port 8000
```

Health and metrics:

- `GET /healthz`
- `GET /metrics` (requires an OPS API key)

## Ingestion (positions, limits, FX, reference)

Ingestion is queued and processed by workers. At a minimum you need:

1. A scheduler to enqueue stale jobs
2. A worker to process `positions`, `limits`, and `reference` jobs

Example wiring (fixture adapters shown):

```python
from datetime import datetime, timezone

from tradepilot.config import settings
from tradepilot.db.session import SessionLocal
from tradepilot.ingest.adapters.factory import build_fx_adapter, build_limits_adapter, build_reference_adapter
from tradepilot.ingest.adapters.positions_db import PositionsDbAdapter
from tradepilot.ingest.enqueuer import IngestEnqueuer
from tradepilot.ingest.queue import IngestQueue
from tradepilot.ingest.repository import IngestRepository
from tradepilot.ingest.reference_repository import ReferenceRepository
from tradepilot.ingest.worker import IngestWorker

queue = IngestQueue(session_factory=SessionLocal)
enqueuer = IngestEnqueuer(session_factory=SessionLocal, queue=queue)
worker = IngestWorker(
    session_factory=SessionLocal,
    queue=queue,
    repository=IngestRepository(session_factory=SessionLocal),
    positions_adapter=PositionsDbAdapter(settings.positions_view, SessionLocal),
    limits_adapter=build_limits_adapter(settings),
    fx_adapter=build_fx_adapter(settings),
    reference_adapter=build_reference_adapter(settings),
    reference_repository=ReferenceRepository(session_factory=SessionLocal),
)

# enqueue due jobs
enqueuer.enqueue_due(datetime.now(tz=timezone.utc).isoformat())

# process one job per call
worker.run_once("positions")
worker.run_once("limits")
worker.run_once("reference")
```

You can also trigger ingestion on demand:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/poke \
  -H "X-API-Key: local-ops-key" \
  -H "X-Ingest-Secret: ${TRADEPILOT_INGEST_POKE_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-1","book_id":"book-1","data_type":"positions"}'
```

## Staging trades

```bash
curl -X POST http://localhost:8000/api/v1/trades/stage \
  -H "X-API-Key: local-ops-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-1",
    "book_id": "book-1",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 100,
    "price": 187.50,
    "order_type": "market",
    "override_requested": false
  }'
```

If positions/limits are stale, the API will block by default. To use an override:

```json
{
  "override_requested": true,
  "override_reason": "reduce risk exposure"
}
```

Overrides require an OPS or RISK role and are capped by `TRADEPILOT_OVERRIDE_*` settings.

## Tests

```bash
.venv/bin/python -m pytest -v
```
