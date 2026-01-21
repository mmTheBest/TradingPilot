from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/query", tags=["query"])


@router.get("/book")

def query_book(book_id: str):
    return {"book_id": book_id, "summary": "not implemented"}
