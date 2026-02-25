import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_get_list_vehicle():
    vin = str(uuid.uuid4()).replace("-", "")[:17].upper()

    payload = {"vin": vin, "make": "Ford", "model": "F-150", "year": 2024}
    r = client.post("/api/v1/vehicles", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["vin"] == vin
    vid = created["id"]

    r2 = client.get(f"/api/v1/vehicles/{vid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == vid

    r3 = client.get("/api/v1/vehicles?limit=10&offset=0")
    assert r3.status_code == 200
    assert isinstance(r3.json(), list)

def test_duplicate_vin_returns_409():
    vin = str(uuid.uuid4()).replace("-", "")[:17].upper()
    payload = {"vin": vin, "make": "GM", "model": "Silverado", "year": 2023}

    r1 = client.post("/api/v1/vehicles", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/vehicles", json=payload)
    assert r2.status_code == 409