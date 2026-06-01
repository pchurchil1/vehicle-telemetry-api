import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def _username(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def test_jwt_login_and_role_based_access():
    previous_auth_enabled = settings.auth_enabled
    settings.auth_enabled = False
    admin_username = _username("admin")
    engineer_username = _username("engineer")
    viewer_username = _username("viewer")

    try:
        bootstrap = client.post(
            "/api/v1/auth/bootstrap",
            json={"username": admin_username, "password": "password123", "role": "admin"},
        )
        assert bootstrap.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={"username": admin_username, "password": "password123"},
        )
        assert login.status_code == 200
        admin_token = login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        settings.auth_enabled = True

        create_engineer = client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={"username": engineer_username, "password": "password123", "role": "engineer"},
        )
        assert create_engineer.status_code == 201

        create_viewer = client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={"username": viewer_username, "password": "password123", "role": "viewer"},
        )
        assert create_viewer.status_code == 201

        viewer_login = client.post(
            "/api/v1/auth/login",
            json={"username": viewer_username, "password": "password123"},
        )
        assert viewer_login.status_code == 200
        viewer_headers = {"Authorization": f"Bearer {viewer_login.json()['access_token']}"}

        unauthorized = client.get("/api/v1/vehicles")
        assert unauthorized.status_code == 401

        allowed_read = client.get("/api/v1/vehicles", headers=viewer_headers)
        assert allowed_read.status_code == 200

        denied_write = client.post(
            "/api/v1/vehicles",
            headers=viewer_headers,
            json={"vin": uuid.uuid4().hex[:17].upper(), "make": "Ford", "model": "F-150", "year": 2024},
        )
        assert denied_write.status_code == 403
        assert denied_write.json()["error"] == "insufficient_role"
    finally:
        settings.auth_enabled = previous_auth_enabled
