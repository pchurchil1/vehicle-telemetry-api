from pydantic import BaseModel, Field
from datetime import datetime

class EventCreate(BaseModel):
    vehicle_id: int
    ecu_id: int | None = None
    event_type: str = Field(min_length=1, max_length=80)
    payload: str = Field(min_length=1, max_length=2000)

class EventOut(BaseModel):
    id: int
    vehicle_id: int
    ecu_id: int | None
    event_type: str
    payload: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TelemetrySummaryOut(BaseModel):
    vehicle_id: int
    ecu_count: int
    event_count: int
    last_event_at: datetime | None
    event_counts_by_type: dict[str, int]
