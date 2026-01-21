from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from tradepilot.auth.dependencies import require_api_key


def test_require_api_key_blocks_missing():
    app = FastAPI()

    @app.get("/secure")
    def secure(_ctx=Depends(require_api_key)):
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/secure").status_code == 401
