from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.event_repo import EventRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.ecu_repo import EcuRepository
from app.schemas.event import EventCreate

class EventService:
    def __init__(self, db: Session):
        self.events = EventRepository(db)
        self.vehicles = VehicleRepository(db)
        self.ecus = EcuRepository(db)

    def create_event(self, data: EventCreate):
        if not self.vehicles.get_by_id(data.vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")

        if data.ecu_id is not None:
            ecu = self.ecus.get_by_id(data.ecu_id)
            if not ecu:
                raise HTTPException(status_code=404, detail="ECU not found")
            if ecu.vehicle_id != data.vehicle_id:
                raise HTTPException(status_code=409, detail="ECU does not belong to vehicle")

        return self.events.create(data)

    def list_events_for_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        event_type: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        if not self.vehicles.get_by_id(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")

        if ecu_id is not None:
            ecu = self.ecus.get_by_id(ecu_id)
            if not ecu:
                raise HTTPException(status_code=404, detail="ECU not found")
            if ecu.vehicle_id != vehicle_id:
                raise HTTPException(status_code=409, detail="ECU does not belong to vehicle")

        if created_after is not None and created_before is not None:
            if created_after > created_before:
                raise HTTPException(status_code=400, detail="created_after must be <= created_before")

        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)

        return self.events.list_by_vehicle(
            vehicle_id=vehicle_id,
            ecu_id=ecu_id,
            event_type=event_type,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset,
        )