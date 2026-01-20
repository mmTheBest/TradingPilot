from tradepilot.db.models import (
    AuditEvent,
    Book,
    FxRateSnapshot,
    IssuerMaster,
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
    assert RiskLimitsVersioned
    assert RiskLimitsSnapshotFull
    assert RiskLimitsDelta
    assert AuditEvent
    assert StagedTradeRecord
    assert TradeApproval
    assert TradeSubmitQueue
    assert SlackApprover
