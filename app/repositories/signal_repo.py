from sqlalchemy.orm import Session

from app.models.signal import Signal
from app.schemas.signal import SignalCreate, SignalUpdate


class SignalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, signal_id: int) -> Signal | None:
        return self.db.get(Signal, signal_id)

    def list_by_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Signal]:
        q = self.db.query(Signal).filter(Signal.vehicle_id == vehicle_id)
        if ecu_id is not None:
            q = q.filter(Signal.ecu_id == ecu_id)
        if name is not None:
            q = q.filter(Signal.name.ilike(name))
        return q.order_by(Signal.id.asc()).offset(offset).limit(limit).all()

    def create(self, data: SignalCreate) -> Signal:
        signal = Signal(**data.model_dump())
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)
        return signal

    def update(self, signal: Signal, data: SignalUpdate) -> Signal:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(signal, field, value)
        self.db.commit()
        self.db.refresh(signal)
        return signal

    def delete(self, signal: Signal) -> None:
        self.db.delete(signal)
        self.db.commit()
