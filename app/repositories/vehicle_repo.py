from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate

class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self.db.get(Vehicle, vehicle_id)

    def get_by_vin(self, vin: str) -> Vehicle | None:
        return self.db.query(Vehicle).filter(Vehicle.vin == vin).first()

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        vin_prefix: str | None = None,
    ) -> list[Vehicle]:
        q = self.db.query(Vehicle)

        if make is not None:
            q = q.filter(Vehicle.make.ilike(make))
        if model is not None:
            q = q.filter(Vehicle.model.ilike(model))
        if year is not None:
            q = q.filter(Vehicle.year == year)
        if vin_prefix is not None:
            q = q.filter(Vehicle.vin.ilike(f"{vin_prefix}%"))

        return q.order_by(Vehicle.id.asc()).offset(offset).limit(limit).all()

    def create(self, data: VehicleCreate) -> Vehicle:
        v = Vehicle(**data.model_dump())
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return v

    def update(self, vehicle: Vehicle, data: VehicleUpdate) -> Vehicle:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle

    def delete(self, vehicle: Vehicle) -> None:
        self.db.delete(vehicle)
        self.db.commit()
