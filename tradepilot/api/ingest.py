from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel

from tradepilot.auth.dependencies import require_role
from tradepilot.config import settings
from tradepilot.db.session import SessionLocal
from tradepilot.ingest.queue import IngestQueue

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


class PokeRequest(BaseModel):
    tenant_id: str
    book_id: str
    data_type: str


@router.post("/poke")
def poke_ingest(
    request: PokeRequest,
    x_ingest_secret: str = Header(default=""),
    _auth=Depends(require_role({"OPS"})),
):
    if x_ingest_secret != settings.ingest_poke_secret:
        raise HTTPException(status_code=401, detail="unauthorized")
    queue = IngestQueue(session_factory=SessionLocal)
    queue.enqueue(request.tenant_id, request.book_id, request.data_type, reason="poke")
    return {"status": "enqueued"}
