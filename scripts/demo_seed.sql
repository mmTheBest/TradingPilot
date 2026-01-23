-- Demo seed data for local quickstart.
-- Safe to re-run.

INSERT INTO books (id, tenant_id, portfolio_id, desk_id, base_currency)
VALUES ('book-demo', 'tenant-demo', 'portfolio-demo', 'desk-demo', 'USD')
ON CONFLICT (id) DO NOTHING;

INSERT INTO issuer_master (issuer_id, legal_name)
VALUES ('issuer-demo', 'Demo Issuer Inc.')
ON CONFLICT (issuer_id) DO NOTHING;

INSERT INTO sector_taxonomy (taxonomy_id, taxonomy_version, vendor, effective_from)
VALUES (
  'taxonomy-demo',
  'v1',
  'demo',
  to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
)
ON CONFLICT (taxonomy_id) DO NOTHING;

INSERT INTO security_master (symbol, issuer_id, sector_id, taxonomy_id, updated_at)
VALUES (
  'AAPL',
  'issuer-demo',
  'sector-demo',
  'taxonomy-demo',
  to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
)
ON CONFLICT (symbol) DO NOTHING;

INSERT INTO api_keys (id, tenant_id, role, owner, key_hash, created_at)
VALUES ('demo-ops-key', 'tenant-demo', 'OPS', 'demo', 'demo', to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'))
ON CONFLICT (id) DO NOTHING;

INSERT INTO positions_snapshot_full (
  id,
  tenant_id,
  book_id,
  as_of_ts,
  net_exposure,
  gross_notional,
  snapshot_json,
  payload_hash
)
VALUES (
  'positions-demo',
  'tenant-demo',
  'book-demo',
  to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
  187500.0,
  187500.0,
  '[{"symbol":"AAPL","quantity":1000,"price":187.5}]'::jsonb,
  repeat('0', 64)
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO risk_limits_versioned (
  id,
  version_id,
  tenant_id,
  book_id,
  dimension,
  dimension_id,
  absolute_limit,
  relative_limit_pct,
  effective_from,
  effective_to
)
VALUES
  (
    'limits-book-demo',
    'limits-v1',
    'tenant-demo',
    'book-demo',
    'book',
    'book-demo',
    5000000.0,
    0.50,
    to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
    NULL
  ),
  (
    'limits-issuer-demo',
    'limits-v1',
    'tenant-demo',
    'book-demo',
    'issuer',
    'issuer-demo',
    2000000.0,
    0.20,
    to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
    NULL
  ),
  (
    'limits-sector-demo',
    'limits-v1',
    'tenant-demo',
    'book-demo',
    'sector',
    'sector-demo',
    3000000.0,
    0.30,
    to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
    NULL
  )
ON CONFLICT ON CONSTRAINT uq_limits_version_row DO NOTHING;

INSERT INTO limits_snapshot_full (id, tenant_id, book_id, as_of_ts, version_id, payload_hash)
VALUES (
  'limits-snapshot-demo',
  'tenant-demo',
  'book-demo',
  to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
  'limits-v1',
  repeat('1', 64)
)
ON CONFLICT (id) DO NOTHING;
