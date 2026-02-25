from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.event import EventCreate, EventOut
from app.services.event_service import EventService

router = APIRouter()

@router.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    return EventService(db).create_event(payload)

@router.get("/vehicles/{vehicle_id}/events", response_model=list[EventOut])
def list_events_for_vehicle(
    vehicle_id: int,
    ecu_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return EventService(db).list_events_for_vehicle(
        vehicle_id=vehicle_id,
        ecu_id=ecu_id,
        limit=limit,
        offset=offset,
    )