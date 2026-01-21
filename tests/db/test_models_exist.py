from tradepilot.db.models import (
    AuditEvent,
    ApiKey,
    Book,
    FxRateSnapshot,
    IngestRefreshQueue,
    IngestRun,
    IssuerMaster,
    MarketNewsItem,
    PositionsDelta,
    PositionsSnapshotFull,
    RiskLimitsDelta,
    RiskLimitsSnapshotFull,
    RiskLimitsVersioned,
    SecurityMaster,
    SlackApprover,
    SectorTaxonomy,
    StagedTradeRecord,
    Tenant,
    TradeApproval,
    TradeSubmitQueue,
)


def test_models_importable():
    assert Tenant
    assert Book
    assert SecurityMaster
    assert IssuerMaster
    assert SectorTaxonomy
    assert FxRateSnapshot
    assert PositionsSnapshotFull
    assert PositionsDelta
    assert hasattr(PositionsSnapshotFull, "snapshot_json")
    assert hasattr(PositionsSnapshotFull, "payload_hash")
    assert hasattr(PositionsDelta, "ops_json")
    assert hasattr(PositionsDelta, "payload_hash")
    assert hasattr(PositionsDelta, "op_count")
    assert RiskLimitsVersioned
    assert RiskLimitsSnapshotFull
    assert RiskLimitsDelta
    assert hasattr(RiskLimitsSnapshotFull, "version_id")
    assert hasattr(RiskLimitsSnapshotFull, "payload_hash")
    assert hasattr(RiskLimitsDelta, "summary_json")
    assert AuditEvent
    assert ApiKey
    assert MarketNewsItem
    assert StagedTradeRecord
    assert TradeApproval
    assert TradeSubmitQueue
    assert SlackApprover
    assert IngestRun
    assert IngestRefreshQueue
