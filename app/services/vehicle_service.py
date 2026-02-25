from sqlalchemy.orm import Session
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.vehicle import VehicleCreate
from fastapi import HTTPException

class VehicleService:
    def __init__(self, db: Session):
        self.repo = VehicleRepository(db)

    def create_vehicle(self, data: VehicleCreate):
        if self.repo.get_by_vin(data.vin):
            raise HTTPException(status_code=409, detail="VIN already exists")
        return self.repo.create(data)

    def get_vehicle(self, vehicle_id: int):
        v = self.repo.get_by_id(vehicle_id)
        if not v:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return v

    def list_vehicles(self, limit: int = 50, offset: int = 0):
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return self.repo.list(limit=limit, offset=offset)