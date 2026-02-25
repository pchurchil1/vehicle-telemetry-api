import time
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from urllib.parse import quote

client = TestClient(app)

def _new_vin() -> str:
    return str(uuid.uuid4()).replace("-", "")[:17].upper()

def _create_vehicle() -> int:
    payload = {"vin": _new_vin(), "make": "Ford", "model": "Fusion", "year": 2020}
    r = client.post("/api/v1/vehicles", json=payload)
    assert r.status_code == 201
    return r.json()["id"]

def test_event_type_filter_and_date_range():
    vehicle_id = _create_vehicle()

    # Create two events with different types
    r1 = client.post("/api/v1/events", json={
        "vehicle_id": vehicle_id, "ecu_id": None, "event_type": "DTC", "payload": "P0300"
    })
    assert r1.status_code == 201

    # Ensure created_at differs (avoid same-timestamp edge cases)
    time.sleep(0.05)

    r2 = client.post("/api/v1/events", json={
        "vehicle_id": vehicle_id, "ecu_id": None, "event_type": "INFO", "payload": "boot"
    })
    assert r2.status_code == 201

    # Filter by event_type
    rf = client.get(f"/api/v1/vehicles/{vehicle_id}/events?event_type=DTC&limit=50&offset=0")
    assert rf.status_code == 200
    events = rf.json()
    assert len(events) >= 1
    assert all(e["event_type"] == "DTC" for e in events)

    # Date filter: created_after = now-1min should include both
    created_after = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    created_after_q = quote(created_after, safe="")  # encode +, :, etc.

    rd = client.get(
        f"/api/v1/vehicles/{vehicle_id}/events?created_after={created_after_q}&limit=50&offset=0"
    )
    assert rd.status_code == 200
    assert len(rd.json()) >= 2