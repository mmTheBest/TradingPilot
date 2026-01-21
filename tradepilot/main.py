from fastapi import Depends, FastAPI, Response

from tradepilot.api.chatops import router as chatops_router
from tradepilot.api.ingest import router as ingest_router
from tradepilot.api.query import router as query_router
from tradepilot.api.trades import router as trades_router
from tradepilot.auth.dependencies import require_role
from tradepilot.logging import configure_logging
from tradepilot.metrics import metrics_payload

app = FastAPI()
configure_logging()
app.include_router(chatops_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(trades_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics(_auth=Depends(require_role({"OPS"}))):
    return Response(metrics_payload(), media_type="text/plain")
