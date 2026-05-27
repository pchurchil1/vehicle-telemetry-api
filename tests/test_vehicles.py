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

def test_update_delete_and_filter_vehicle():
    vin = str(uuid.uuid4()).replace("-", "")[:17].upper()
    payload = {"vin": vin, "make": "Ford", "model": "F-150", "year": 2024}
    created = client.post("/api/v1/vehicles", json=payload)
    assert created.status_code == 201
    vehicle_id = created.json()["id"]

    updated = client.patch(f"/api/v1/vehicles/{vehicle_id}", json={"model": "Ranger", "year": 2025})
    assert updated.status_code == 200
    assert updated.json()["model"] == "Ranger"
    assert updated.json()["year"] == 2025

    filtered = client.get(f"/api/v1/vehicles?make=Ford&model=Ranger&year=2025&vin_prefix={vin[:6]}")
    assert filtered.status_code == 200
    assert any(v["id"] == vehicle_id for v in filtered.json())

    deleted = client.delete(f"/api/v1/vehicles/{vehicle_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/vehicles/{vehicle_id}")
    assert missing.status_code == 404

def test_duplicate_vin_returns_409():
    vin = str(uuid.uuid4()).replace("-", "")[:17].upper()
    payload = {"vin": vin, "make": "GM", "model": "Silverado", "year": 2023}

    r1 = client.post("/api/v1/vehicles", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/vehicles", json=payload)
    assert r2.status_code == 409
