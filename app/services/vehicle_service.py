from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
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

    def update_vehicle(self, vehicle_id: int, data: VehicleUpdate):
        vehicle = self.get_vehicle(vehicle_id)
        if data.vin is not None and data.vin != vehicle.vin:
            if self.repo.get_by_vin(data.vin):
                raise HTTPException(status_code=409, detail="VIN already exists")
        try:
            return self.repo.update(vehicle, data)
        except IntegrityError:
            raise HTTPException(status_code=409, detail="VIN already exists")

    def delete_vehicle(self, vehicle_id: int):
        vehicle = self.get_vehicle(vehicle_id)
        self.repo.delete(vehicle)
        return None

    def list_vehicles(
        self,
        limit: int = 50,
        offset: int = 0,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        vin_prefix: str | None = None,
    ):
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return self.repo.list(
            limit=limit,
            offset=offset,
            make=make,
            model=model,
            year=year,
            vin_prefix=vin_prefix,
        )
