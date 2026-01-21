from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from tradepilot.config import settings
from tradepilot.db.session import SessionLocal
from tradepilot.ingest.queue import IngestQueue

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


class PokeRequest(BaseModel):
    tenant_id: str
    book_id: str
    data_type: str


@router.post("/poke")
def poke_ingest(request: PokeRequest, x_ingest_secret: str = Header(default="")):
    if x_ingest_secret != settings.ingest_poke_secret:
        raise HTTPException(status_code=401, detail="unauthorized")
    queue = IngestQueue(session_factory=SessionLocal)
    queue.enqueue(request.tenant_id, request.book_id, request.data_type, reason="poke")
    return {"status": "enqueued"}
