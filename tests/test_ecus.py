import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _new_vin() -> str:
    return str(uuid.uuid4()).replace("-", "")[:17].upper()

def test_create_get_list_ecu():
    # Create vehicle
    v = {"vin": _new_vin(), "make": "Ford", "model": "Escape", "year": 2022}
    rv = client.post("/api/v1/vehicles", json=v)
    assert rv.status_code == 201
    vehicle_id = rv.json()["id"]

    # Create ECU
    ecu_payload = {"vehicle_id": vehicle_id, "name": "ECM", "supplier": "Bosch"}
    r1 = client.post("/api/v1/ecus", json=ecu_payload)
    assert r1.status_code == 201
    ecu_id = r1.json()["id"]
    assert r1.json()["vehicle_id"] == vehicle_id

    # Get ECU
    r2 = client.get(f"/api/v1/ecus/{ecu_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == ecu_id

    # List ECUs for vehicle
    r3 = client.get(f"/api/v1/vehicles/{vehicle_id}/ecus?limit=10&offset=0")
    assert r3.status_code == 200
    assert any(e["id"] == ecu_id for e in r3.json())

def test_create_ecu_vehicle_not_found_404():
    ecu_payload = {"vehicle_id": 9999999, "name": "TCM", "supplier": "Continental"}
    r = client.post("/api/v1/ecus", json=ecu_payload)
    assert r.status_code == 404

def test_duplicate_ecu_name_same_vehicle_returns_409():
    v = {"vin": _new_vin(), "make": "Ford", "model": "Edge", "year": 2021}
    rv = client.post("/api/v1/vehicles", json=v)
    assert rv.status_code == 201
    vehicle_id = rv.json()["id"]

    ecu_payload = {"vehicle_id": vehicle_id, "name": "ECM", "supplier": "Bosch"}
    r1 = client.post("/api/v1/ecus", json=ecu_payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/ecus", json=ecu_payload)
    assert r2.status_code == 409