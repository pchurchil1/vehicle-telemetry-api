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
    ev = {
        "vehicle_id": vehicle_id,
        "ecu_id": ecu_id,
        "event_type": "DTC",
        "payload": {"code": "P0300", "severity": "warning"},
    }
    r1 = client.post("/api/v1/events", json=ev)
    assert r1.status_code == 201
    created = r1.json()
    assert created["vehicle_id"] == vehicle_id
    assert created["ecu_id"] == ecu_id
    assert created["payload"]["code"] == "P0300"

    # List events for vehicle
    r2 = client.get(f"/api/v1/vehicles/{vehicle_id}/events?limit=10&offset=0")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1

    # List events filtered by ECU
    r3 = client.get(f"/api/v1/vehicles/{vehicle_id}/events?ecu_id={ecu_id}&limit=10&offset=0")
    assert r3.status_code == 200
    assert all(e["ecu_id"] == ecu_id for e in r3.json())

def test_get_event_by_id():
    vehicle_id = _create_vehicle()
    ev = {"vehicle_id": vehicle_id, "ecu_id": None, "event_type": "INFO", "payload": {"message": "boot"}}
    created = client.post("/api/v1/events", json=ev)
    assert created.status_code == 201
    event_id = created.json()["id"]

    fetched = client.get(f"/api/v1/events/{event_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == event_id

def test_get_event_not_found_404():
    r = client.get("/api/v1/events/9999999")
    assert r.status_code == 404

def test_vehicle_telemetry_summary():
    vehicle_id = _create_vehicle()
    ecu_id = _create_ecu(vehicle_id)

    dtc = {"vehicle_id": vehicle_id, "ecu_id": ecu_id, "event_type": "DTC", "payload": {"code": "P0300"}}
    info = {"vehicle_id": vehicle_id, "ecu_id": None, "event_type": "INFO", "payload": {"message": "boot"}}
    assert client.post("/api/v1/events", json=dtc).status_code == 201
    assert client.post("/api/v1/events", json=dtc).status_code == 201
    assert client.post("/api/v1/events", json=info).status_code == 201

    r = client.get(f"/api/v1/vehicles/{vehicle_id}/telemetry/summary")
    assert r.status_code == 200
    summary = r.json()
    assert summary["vehicle_id"] == vehicle_id
    assert summary["ecu_count"] == 1
    assert summary["event_count"] == 3
    assert summary["last_event_at"] is not None
    assert summary["event_counts_by_type"] == {"DTC": 2, "INFO": 1}

def test_vehicle_telemetry_summary_vehicle_not_found_404():
    r = client.get("/api/v1/vehicles/9999999/telemetry/summary")
    assert r.status_code == 404

def test_event_vehicle_not_found_404():
    ev = {"vehicle_id": 9999999, "ecu_id": None, "event_type": "INFO", "payload": {"message": "hello"}}
    r = client.post("/api/v1/events", json=ev)
    assert r.status_code == 404
    assert r.json() == {
        "error": "vehicle_not_found",
        "message": "Vehicle not found",
        "status_code": 404,
    }

def test_batch_event_ingestion_accepts_valid_and_reports_rejected():
    vehicle_id = _create_vehicle()

    r = client.post("/api/v1/events/batch", json={
        "events": [
            {"vehicle_id": vehicle_id, "ecu_id": None, "event_type": "INFO", "payload": {"message": "boot"}},
            {"vehicle_id": 9999999, "ecu_id": None, "event_type": "INFO", "payload": {"message": "missing"}},
        ]
    })
    assert r.status_code == 207
    body = r.json()
    assert body["accepted_count"] == 1
    assert body["rejected_count"] == 1
    assert body["events"][0]["vehicle_id"] == vehicle_id
    assert body["rejected"][0]["index"] == 1
    assert body["rejected"][0]["error"] == "vehicle_not_found"

def test_event_ecu_must_belong_to_vehicle_409():
    vehicle_a = _create_vehicle(make="Ford", model="A", year=2021)
    vehicle_b = _create_vehicle(make="Ford", model="B", year=2021)

    ecu_on_a = _create_ecu(vehicle_a, name="BCM")

    # Attempt to create event for vehicle B using ECU from vehicle A
    ev = {"vehicle_id": vehicle_b, "ecu_id": ecu_on_a, "event_type": "DTC", "payload": {"code": "U0100"}}
    r = client.post("/api/v1/events", json=ev)
    assert r.status_code == 409
