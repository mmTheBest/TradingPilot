from fastapi import FastAPI

from tradepilot.logging import configure_logging

app = FastAPI()
configure_logging()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
