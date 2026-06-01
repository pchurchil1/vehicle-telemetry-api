from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("vehicle_id", "name", name="uq_signal_vehicle_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True, nullable=False)
    ecu_id: Mapped[int | None] = mapped_column(ForeignKey("ecus.id"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    data_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    vehicle = relationship("Vehicle", back_populates="signals")
    ecu = relationship("Ecu", back_populates="signals")
    events = relationship("Event", back_populates="signal")
