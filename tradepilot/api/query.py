from fastapi import APIRouter, Depends, HTTPException

from tradepilot.db.session import SessionLocal
from tradepilot.trades.query_service import QueryService

router = APIRouter(prefix="/api/v1/query", tags=["query"])


@router.get("/book")

def query_book(book_id: str, tenant_id: str, service: QueryService = Depends(lambda: QueryService(SessionLocal))):
    summary = service.get_book_summary(tenant_id=tenant_id, book_id=book_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="book snapshot not found")
    return summary
