from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.auth import require_api_key
from app.core.db import get_db
from app.schemas.event import EventBatchCreate, EventBatchOut, EventCreate, EventOut, TelemetrySummaryOut
from app.services.event_service import EventService

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    return EventService(db).create_event(payload)

@router.post("/events/batch", response_model=EventBatchOut, status_code=207)
def create_events_batch(payload: EventBatchCreate, db: Session = Depends(get_db)):
    return EventService(db).create_events_batch(payload)

@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return EventService(db).get_event(event_id)

@router.get("/vehicles/{vehicle_id}/events", response_model=list[EventOut])
def list_events_for_vehicle(
    vehicle_id: int,
    ecu_id: int | None = Query(None),
    event_type: str | None = Query(None),
    created_after: datetime | None = Query(None),
    created_before: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return EventService(db).list_events_for_vehicle(
        vehicle_id=vehicle_id,
        ecu_id=ecu_id,
        event_type=event_type,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        offset=offset,
    )

@router.get("/vehicles/{vehicle_id}/telemetry/summary", response_model=TelemetrySummaryOut)
def summarize_vehicle_telemetry(vehicle_id: int, db: Session = Depends(get_db)):
    return EventService(db).summarize_vehicle_telemetry(vehicle_id)
