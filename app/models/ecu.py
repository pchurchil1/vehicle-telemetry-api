from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Ecu(Base):
    __tablename__ = "ecus"
    __table_args__ = (
        UniqueConstraint("vehicle_id", "name", name="uq_ecu_vehicle_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    supplier: Mapped[str] = mapped_column(String(80), nullable=True)

    vehicle = relationship("Vehicle", back_populates="ecus")
    events = relationship("Event", back_populates="ecu", cascade="all, delete-orphan")