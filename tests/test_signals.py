import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _new_vin() -> str:
    return uuid.uuid4().hex[:17].upper()


def _create_vehicle() -> int:
    r = client.post("/api/v1/vehicles", json={"vin": _new_vin(), "make": "Ford", "model": "F-150", "year": 2024})
    assert r.status_code == 201
    return r.json()["id"]


def _create_ecu(vehicle_id: int) -> int:
    r = client.post("/api/v1/ecus", json={"vehicle_id": vehicle_id, "name": "ECM", "supplier": "Bosch"})
    assert r.status_code == 201
    return r.json()["id"]


def test_create_get_list_update_delete_signal():
    vehicle_id = _create_vehicle()
    ecu_id = _create_ecu(vehicle_id)

    created = client.post(
        "/api/v1/signals",
        json={
            "vehicle_id": vehicle_id,
            "ecu_id": ecu_id,
            "name": "engine_rpm",
            "unit": "rpm",
            "data_type": "integer",
            "description": "Engine speed",
        },
    )
    assert created.status_code == 201
    signal_id = created.json()["id"]

    fetched = client.get(f"/api/v1/signals/{signal_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "engine_rpm"

    listed = client.get(f"/api/v1/vehicles/{vehicle_id}/signals?ecu_id={ecu_id}&name=engine_rpm")
    assert listed.status_code == 200
    assert any(signal["id"] == signal_id for signal in listed.json())

    updated = client.patch(f"/api/v1/signals/{signal_id}", json={"unit": "rev/min", "description": "Updated"})
    assert updated.status_code == 200
    assert updated.json()["unit"] == "rev/min"

    deleted = client.delete(f"/api/v1/signals/{signal_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/signals/{signal_id}")
    assert missing.status_code == 404


def test_event_can_reference_signal():
    vehicle_id = _create_vehicle()
    ecu_id = _create_ecu(vehicle_id)
    signal = client.post(
        "/api/v1/signals",
        json={"vehicle_id": vehicle_id, "ecu_id": ecu_id, "name": "battery_voltage", "unit": "V", "data_type": "float"},
    )
    assert signal.status_code == 201
    signal_id = signal.json()["id"]

    event = client.post(
        "/api/v1/events",
        json={
            "vehicle_id": vehicle_id,
            "ecu_id": ecu_id,
            "signal_id": signal_id,
            "event_type": "SIGNAL_SAMPLE",
            "payload": {"value": 12.4},
        },
    )
    assert event.status_code == 201
    assert event.json()["signal_id"] == signal_id

    listed = client.get(f"/api/v1/vehicles/{vehicle_id}/events?signal_id={signal_id}")
    assert listed.status_code == 200
    assert all(item["signal_id"] == signal_id for item in listed.json())
