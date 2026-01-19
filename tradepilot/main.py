from fastapi import FastAPI

from tradepilot.api.chatops import router as chatops_router
from tradepilot.logging import configure_logging

app = FastAPI()
configure_logging()
app.include_router(chatops_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
