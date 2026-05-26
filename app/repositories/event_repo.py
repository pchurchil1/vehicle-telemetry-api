from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: int) -> Event | None:
        return self.db.get(Event, event_id)

    def count_by_vehicle(self, vehicle_id: int) -> int:
        return (
            self.db.query(func.count(Event.id))
            .filter(Event.vehicle_id == vehicle_id)
            .scalar()
            or 0
        )

    def latest_created_at_by_vehicle(self, vehicle_id: int) -> datetime | None:
        return (
            self.db.query(func.max(Event.created_at))
            .filter(Event.vehicle_id == vehicle_id)
            .scalar()
        )

    def count_by_type_for_vehicle(self, vehicle_id: int) -> dict[str, int]:
        rows = (
            self.db.query(Event.event_type, func.count(Event.id))
            .filter(Event.vehicle_id == vehicle_id)
            .group_by(Event.event_type)
            .order_by(Event.event_type.asc())
            .all()
        )
        return {event_type: count for event_type, count in rows}

    def list_by_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        event_type: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]:
        q = self.db.query(Event).filter(Event.vehicle_id == vehicle_id)

        if ecu_id is not None:
            q = q.filter(Event.ecu_id == ecu_id)

        if event_type is not None:
            q = q.filter(Event.event_type == event_type)

        if created_after is not None:
            q = q.filter(Event.created_at >= created_after)

        if created_before is not None:
            q = q.filter(Event.created_at <= created_before)

        return (
            q.order_by(Event.created_at.desc(), Event.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, data: EventCreate) -> Event:
        ev = Event(**data.model_dump())
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev
