import time
import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_background_event_ingestion_job_completes():
    vehicle = client.post(
        "/api/v1/vehicles",
        json={"vin": uuid.uuid4().hex[:17].upper(), "make": "GM", "model": "Sierra", "year": 2025},
    )
    assert vehicle.status_code == 201
    vehicle_id = vehicle.json()["id"]

    queued = client.post(
        "/api/v1/ingestion/events",
        json={
            "events": [
                {
                    "vehicle_id": vehicle_id,
                    "ecu_id": None,
                    "signal_id": None,
                    "event_type": "INFO",
                    "payload": {"message": "boot"},
                },
                {
                    "vehicle_id": 9999999,
                    "ecu_id": None,
                    "signal_id": None,
                    "event_type": "INFO",
                    "payload": {"message": "missing"},
                },
            ]
        },
    )
    assert queued.status_code == 202
    job_id = queued.json()["id"]

    body = None
    for _ in range(50):
        status = client.get(f"/api/v1/ingestion/jobs/{job_id}")
        assert status.status_code == 200
        body = status.json()
        if body["status"] in {"completed", "failed"}:
            break
        time.sleep(0.02)

    assert body is not None
    assert body["status"] == "completed"
    assert body["accepted_count"] == 1
    assert body["rejected_count"] == 1

    events = client.get(f"/api/v1/vehicles/{vehicle_id}/events")
    assert events.status_code == 200
    assert any(event["payload"]["message"] == "boot" for event in events.json())
