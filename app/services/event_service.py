from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.errors import error_payload
from app.repositories.event_repo import EventRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.ecu_repo import EcuRepository
from app.repositories.signal_repo import SignalRepository
from app.schemas.event import EventBatchCreate, EventBatchOut, EventBatchRejected, EventCreate, TelemetrySummaryOut

class EventService:
    def __init__(self, db: Session):
        self.events = EventRepository(db)
        self.vehicles = VehicleRepository(db)
        self.ecus = EcuRepository(db)
        self.signals = SignalRepository(db)

    def create_event(self, data: EventCreate):
        if not self.vehicles.get_by_id(data.vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")

        if data.ecu_id is not None:
            ecu = self.ecus.get_by_id(data.ecu_id)
            if not ecu:
                raise HTTPException(status_code=404, detail="ECU not found")
            if ecu.vehicle_id != data.vehicle_id:
                raise HTTPException(status_code=409, detail="ECU does not belong to vehicle")

        if data.signal_id is not None:
            signal = self.signals.get_by_id(data.signal_id)
            if not signal:
                raise HTTPException(status_code=404, detail="Signal not found")
            if signal.vehicle_id != data.vehicle_id:
                raise HTTPException(status_code=409, detail="Signal does not belong to vehicle")
            if data.ecu_id is not None and signal.ecu_id is not None and signal.ecu_id != data.ecu_id:
                raise HTTPException(status_code=409, detail="Signal does not belong to ECU")

        return self.events.create(data)

    def create_events_batch(self, data: EventBatchCreate) -> EventBatchOut:
        accepted = []
        rejected = []

        for index, event_data in enumerate(data.events):
            try:
                accepted.append(self.create_event(event_data))
            except HTTPException as exc:
                message = str(exc.detail)
                payload = error_payload(exc.status_code, message)
                rejected.append(
                    EventBatchRejected(
                        index=index,
                        status_code=exc.status_code,
                        error=payload["error"],
                        message=message,
                    )
                )

        return EventBatchOut(
            accepted_count=len(accepted),
            rejected_count=len(rejected),
            events=accepted,
            rejected=rejected,
        )

    def get_event(self, event_id: int):
        event = self.events.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    def list_events_for_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        signal_id: int | None = None,
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

        if signal_id is not None:
            signal = self.signals.get_by_id(signal_id)
            if not signal:
                raise HTTPException(status_code=404, detail="Signal not found")
            if signal.vehicle_id != vehicle_id:
                raise HTTPException(status_code=409, detail="Signal does not belong to vehicle")

        if created_after is not None and created_before is not None:
            if created_after > created_before:
                raise HTTPException(status_code=400, detail="created_after must be <= created_before")

        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)

        return self.events.list_by_vehicle(
            vehicle_id=vehicle_id,
            ecu_id=ecu_id,
            signal_id=signal_id,
            event_type=event_type,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset,
        )

    def summarize_vehicle_telemetry(self, vehicle_id: int) -> TelemetrySummaryOut:
        if not self.vehicles.get_by_id(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")

        return TelemetrySummaryOut(
            vehicle_id=vehicle_id,
            ecu_count=self.ecus.count_by_vehicle(vehicle_id),
            event_count=self.events.count_by_vehicle(vehicle_id),
            last_event_at=self.events.latest_created_at_by_vehicle(vehicle_id),
            event_counts_by_type=self.events.count_by_type_for_vehicle(vehicle_id),
        )
