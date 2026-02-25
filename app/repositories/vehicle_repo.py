from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate

class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self.db.get(Vehicle, vehicle_id)

    def get_by_vin(self, vin: str) -> Vehicle | None:
        return self.db.query(Vehicle).filter(Vehicle.vin == vin).first()

    def list(self, limit: int = 50, offset: int = 0) -> list[Vehicle]:
        return (
            self.db.query(Vehicle)
            .order_by(Vehicle.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, data: VehicleCreate) -> Vehicle:
        v = Vehicle(**data.model_dump())
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return v