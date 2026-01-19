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
    SectorTaxonomy,
    Tenant,
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
