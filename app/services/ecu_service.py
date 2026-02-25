from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.ecu_repo import EcuRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.ecu import EcuCreate

class EcuService:
    def __init__(self, db: Session):
        self.ecus = EcuRepository(db)
        self.vehicles = VehicleRepository(db)

    def create_ecu(self, data: EcuCreate):
        if not self.vehicles.get_by_id(data.vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return self.ecus.create(data)

    def get_ecu(self, ecu_id: int):
        ecu = self.ecus.get_by_id(ecu_id)
        if not ecu:
            raise HTTPException(status_code=404, detail="ECU not found")
        return ecu

    def list_ecus_for_vehicle(self, vehicle_id: int, limit: int = 50, offset: int = 0):
        if not self.vehicles.get_by_id(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return self.ecus.list_by_vehicle(vehicle_id, limit=limit, offset=offset)