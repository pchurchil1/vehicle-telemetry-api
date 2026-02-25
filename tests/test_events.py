import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _new_vin() -> str:
    return str(uuid.uuid4()).replace("-", "")[:17].upper()

def _create_vehicle(make="GM", model="Truck", year=2023) -> int:
    payload = {"vin": _new_vin(), "make": make, "model": model, "year": year}
    r = client.post("/api/v1/vehicles", json=payload)
    assert r.status_code == 201
    return r.json()["id"]

def _create_ecu(vehicle_id: int, name="ECM") -> int:
    payload = {"vehicle_id": vehicle_id, "name": name, "supplier": "Bosch"}
    r = client.post("/api/v1/ecus", json=payload)
    assert r.status_code == 201
    return r.json()["id"]

def test_create_and_list_events():
    vehicle_id = _create_vehicle()
    ecu_id = _create_ecu(vehicle_id)

    # Create event tied to ECU
    ev = {"vehicle_id": vehicle_id, "ecu_id": ecu_id, "event_type": "DTC", "payload": "P0300"}
    r1 = client.post("/api/v1/events", json=ev)
    assert r1.status_code == 201
    created = r1.json()
    assert created["vehicle_id"] == vehicle_id
    assert created["ecu_id"] == ecu_id

    # List events for vehicle
    r2 = client.get(f"/api/v1/vehicles/{vehicle_id}/events?limit=10&offset=0")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1

    # List events filtered by ECU
    r3 = client.get(f"/api/v1/vehicles/{vehicle_id}/events?ecu_id={ecu_id}&limit=10&offset=0")
    assert r3.status_code == 200
    assert all(e["ecu_id"] == ecu_id for e in r3.json())

def test_event_vehicle_not_found_404():
    ev = {"vehicle_id": 9999999, "ecu_id": None, "event_type": "INFO", "payload": "hello"}
    r = client.post("/api/v1/events", json=ev)
    assert r.status_code == 404

def test_event_ecu_must_belong_to_vehicle_409():
    vehicle_a = _create_vehicle(make="Ford", model="A", year=2021)
    vehicle_b = _create_vehicle(make="Ford", model="B", year=2021)

    ecu_on_a = _create_ecu(vehicle_a, name="BCM")

    # Attempt to create event for vehicle B using ECU from vehicle A
    ev = {"vehicle_id": vehicle_b, "ecu_id": ecu_on_a, "event_type": "DTC", "payload": "U0100"}
    r = client.post("/api/v1/events", json=ev)
    assert r.status_code == 409