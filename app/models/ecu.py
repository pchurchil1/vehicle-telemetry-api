from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Ecu(Base):
    __tablename__ = "ecus"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    supplier: Mapped[str] = mapped_column(String(80), nullable=True)

    vehicle = relationship("Vehicle", back_populates="ecus")
    events = relationship("Event", back_populates="ecu", cascade="all, delete-orphan")