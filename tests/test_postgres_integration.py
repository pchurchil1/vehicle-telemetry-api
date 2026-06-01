import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import engine
from app.main import app


@pytest.mark.postgres
def test_postgres_integration_api_uses_postgres():
    if os.environ.get("RUN_POSTGRES_TESTS") != "1":
        pytest.skip("Set RUN_POSTGRES_TESTS=1 with a PostgreSQL DATABASE_URL to run this test")

    assert engine.dialect.name == "postgresql"

    client = TestClient(app)

    health = client.get("/api/v1/db/health")
    assert health.status_code == 200
    assert health.json() == {"db": "ok"}

    created = client.post(
        "/api/v1/vehicles",
        json={"vin": uuid.uuid4().hex[:17].upper(), "make": "Ford", "model": "F-150", "year": 2026},
    )
    assert created.status_code == 201
