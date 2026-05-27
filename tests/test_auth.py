from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def test_optional_api_key_auth():
    previous_api_key = settings.api_key
    settings.api_key = "secret"
    try:
        unauthorized = client.get("/api/v1/vehicles")
        assert unauthorized.status_code == 401
        assert unauthorized.json()["error"] == "invalid_api_key"

        authorized = client.get("/api/v1/vehicles", headers={"X-API-Key": "secret"})
        assert authorized.status_code == 200
    finally:
        settings.api_key = previous_api_key
