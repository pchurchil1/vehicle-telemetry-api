from sqlalchemy import String, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_vehicle_created", "vehicle_id", "created_at"),
        Index("ix_events_ecu_created", "ecu_id", "created_at"),
        Index("ix_events_event_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True, nullable=False)
    ecu_id: Mapped[int] = mapped_column(ForeignKey("ecus.id"), index=True, nullable=True)

    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle = relationship("Vehicle", back_populates="events")
    ecu = relationship("Ecu", back_populates="events")