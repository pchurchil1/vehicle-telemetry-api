from sqlalchemy.orm import Session
from app.models.ecu import Ecu
from app.schemas.ecu import EcuCreate

class EcuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ecu_id: int) -> Ecu | None:
        return self.db.get(Ecu, ecu_id)

    def list_by_vehicle(self, vehicle_id: int, limit: int = 50, offset: int = 0) -> list[Ecu]:
        return (
            self.db.query(Ecu)
            .filter(Ecu.vehicle_id == vehicle_id)
            .order_by(Ecu.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, data: EcuCreate) -> Ecu:
        ecu = Ecu(**data.model_dump())
        self.db.add(ecu)
        self.db.commit()
        self.db.refresh(ecu)
        return ecu