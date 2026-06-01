from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.ecu_repo import EcuRepository
from app.repositories.signal_repo import SignalRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.signal import SignalCreate, SignalUpdate


class SignalService:
    def __init__(self, db: Session):
        self.signals = SignalRepository(db)
        self.vehicles = VehicleRepository(db)
        self.ecus = EcuRepository(db)

    def _validate_parentage(self, vehicle_id: int, ecu_id: int | None) -> None:
        if not self.vehicles.get_by_id(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        if ecu_id is not None:
            ecu = self.ecus.get_by_id(ecu_id)
            if not ecu:
                raise HTTPException(status_code=404, detail="ECU not found")
            if ecu.vehicle_id != vehicle_id:
                raise HTTPException(status_code=409, detail="ECU does not belong to vehicle")

    def create_signal(self, data: SignalCreate):
        self._validate_parentage(data.vehicle_id, data.ecu_id)
        try:
            return self.signals.create(data)
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Signal name already exists for vehicle")

    def get_signal(self, signal_id: int):
        signal = self.signals.get_by_id(signal_id)
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        return signal

    def update_signal(self, signal_id: int, data: SignalUpdate):
        signal = self.get_signal(signal_id)
        ecu_id = data.ecu_id if "ecu_id" in data.model_fields_set else signal.ecu_id
        self._validate_parentage(signal.vehicle_id, ecu_id)
        try:
            return self.signals.update(signal, data)
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Signal name already exists for vehicle")

    def delete_signal(self, signal_id: int):
        signal = self.get_signal(signal_id)
        self.signals.delete(signal)
        return None

    def list_signals_for_vehicle(
        self,
        vehicle_id: int,
        ecu_id: int | None = None,
        name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        self._validate_parentage(vehicle_id, ecu_id)
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return self.signals.list_by_vehicle(
            vehicle_id=vehicle_id,
            ecu_id=ecu_id,
            name=name,
            limit=limit,
            offset=offset,
        )
