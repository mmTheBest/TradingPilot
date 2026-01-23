# TradePilot

TradePilot is a trading-operations service that stages trades safely. It pulls
positions, risk limits, FX rates, and reference data, then evaluates exposure
and data freshness before allowing an order to proceed. The goal is to make
trade approvals auditable, repeatable, and safe by default.

If you're new to this codebase, start here. This README explains what the
service does, how to install it from GitHub, and how to run it locally.

## Why we built this

Trading teams often rely on fragmented tools and manual checks for pre‑trade
risk and approvals. That creates slow turnarounds, inconsistent decisions, and
audit gaps. TradePilot standardizes the pre‑trade gate so every order is checked
the same way, backed by the same data, and recorded with a clear audit trail.

## Target users

- Trading operations teams
- Risk and compliance teams

## Key features

- **Trade staging with risk checks**: validates exposure, issuer/sector limits,
  liquidity, and best-execution prompts before staging a trade.
- **Freshness gating**: fails closed when positions or limits are stale, with
  explicit override workflows that are logged.
- **Ingestion pipeline**: scheduled and on-demand ingestion of positions, limits,
  FX, and reference data into Postgres with audit trails.
- **Auditability**: stores snapshots, deltas, and staging metadata so decisions
  can be replayed later.
- **Ops integrations**: chatops approvals, metrics, and operational safeguards.

## Tech stack

- **API**: FastAPI
- **Data layer**: PostgreSQL + SQLAlchemy + Alembic
- **Ingestion**: adapter-based pipeline for positions, limits, FX, reference data
- **Observability**: Prometheus metrics
- **Integrations**: Slack/Teams hooks, EMS/OMS staging via EMSX adapter

## Requirements

- Python **3.12+**
- Postgres **14+**

## Quickstart (Docker Compose)

```bash
git clone https://github.com/mmTheBest/TradingPilot.git
cd TradingPilot
git checkout public-release
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Seed demo data (required for first run)

```bash
docker compose exec db psql -U tradepilot -d tradepilot -f /scripts/demo_seed.sql
```

## Install (from GitHub, local Python)

We recommend installing into a virtual environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install "git+https://github.com/mmTheBest/TradingPilot.git@public-release"
```

To pin a specific version or commit:

```bash
.venv/bin/python -m pip install "git+https://github.com/mmTheBest/TradingPilot.git@<tag-or-sha>"
```

## Configuration

TradePilot reads environment variables with the `TRADEPILOT_` prefix (see
`tradepilot/config.py`). Minimal required configuration:

```bash
export TRADEPILOT_DATABASE_URL="postgresql+psycopg://tradepilot:tradepilot@localhost:5432/tradepilot"
export TRADEPILOT_INGEST_POKE_SECRET="change-me"
```

Common optional settings:

```bash
export TRADEPILOT_POSITIONS_VIEW="positions_view"
export TRADEPILOT_LIMITS_ADAPTER_KIND="fixture"   # or "api"
export TRADEPILOT_LIMITS_API_ENDPOINT="http://localhost:9100"
export TRADEPILOT_FX_ADAPTER_KIND="fixture"       # or "api"
export TRADEPILOT_FX_API_ENDPOINT="http://localhost:9200"
export TRADEPILOT_REFERENCE_ADAPTER_KIND="api"
export TRADEPILOT_REFERENCE_API_ENDPOINT="http://localhost:9300"
```

If you use Docker Compose, keep the database host as `db`. If you run locally,
use `localhost` instead.

### Adapter notes

- **fixture** adapters are local and require no external services.
- **api** adapters call external services; set `*_API_ENDPOINT` accordingly.
- Reference data ingestion is optional for the quickstart demo because the demo
  seed data includes a minimal security master.

## Database setup

Run migrations:

```bash
export TRADEPILOT_DATABASE_URL="postgresql+psycopg://tradepilot:tradepilot@localhost:5432/tradepilot"
alembic upgrade head
```

Seed at least one book and API key so ingestion and API calls work:

```bash
psql postgresql://tradepilot:tradepilot@localhost:5432/tradepilot -f scripts/demo_seed.sql
```

The demo API key is `demo-ops-key`. Use it as the `X-API-Key` header.

## Running the API

```bash
uvicorn tradepilot.main:app --reload --port 8000
```

Endpoints:

- `GET /healthz`
- `GET /metrics` (requires an OPS API key)
- `POST /api/v1/trades/stage`
- `POST /api/v1/ingest/poke`

## Ingestion (positions, limits, FX, reference)

Ingestion is queued and processed by workers. At a minimum you need:

1. A scheduler to enqueue stale jobs
2. A worker to process `positions` and `limits` jobs

For the quickstart demo, you can skip ingestion and use the seeded snapshots.
For real environments, run the scheduler and workers on an interval.

Example wiring:

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
worker.run_once("reference")  # optional
```

You can also trigger ingestion on demand:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/poke \
  -H "X-API-Key: demo-ops-key" \
  -H "X-Ingest-Secret: ${TRADEPILOT_INGEST_POKE_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-demo","book_id":"book-demo","data_type":"positions"}'
```

## Staging trades

```bash
curl -X POST http://localhost:8000/api/v1/trades/stage \
  -H "X-API-Key: demo-ops-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-demo",
    "book_id": "book-demo",
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
