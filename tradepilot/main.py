from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from tradepilot.api.chatops import router as chatops_router
from tradepilot.api.ingest import router as ingest_router
from tradepilot.api.query import router as query_router
from tradepilot.api.trades import router as trades_router
from tradepilot.auth.dependencies import require_role
from tradepilot.config import settings
from tradepilot.api.middleware import RateLimitMiddleware, RequestSizeLimitMiddleware
from tradepilot.logging import configure_logging
from tradepilot.metrics import metrics_payload

app = FastAPI()
configure_logging()
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimitMiddleware)
origins = ["*"] if settings.cors_origins == "*" else [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
