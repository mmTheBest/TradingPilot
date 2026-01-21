from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from tradepilot.auth.dependencies import require_role


def test_require_role_blocks():
    app = FastAPI()

    @app.get("/secure")
    def secure(_ctx=Depends(require_role({"RISK"}))):
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/secure")
    assert response.status_code == 401
