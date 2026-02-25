from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: int) -> Event | None:
        return self.db.get(Event, event_id)

    def list_by_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]:
        q = self.db.query(Event).filter(Event.vehicle_id == vehicle_id)
        if ecu_id is not None:
            q = q.filter(Event.ecu_id == ecu_id)

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