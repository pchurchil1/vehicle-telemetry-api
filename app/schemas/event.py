from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime

class EventCreate(BaseModel):
    vehicle_id: int = Field(json_schema_extra={"example": 1})
    ecu_id: int | None = Field(default=None, json_schema_extra={"example": 1})
    signal_id: int | None = Field(default=None, json_schema_extra={"example": 1})
    event_type: str = Field(
        min_length=1,
        max_length=80,
        json_schema_extra={"example": "DTC"},
    )
    payload: dict[str, Any] = Field(
        min_length=1,
        json_schema_extra={
            "example": {
                "code": "P0300",
                "severity": "warning",
                "odometer_miles": 42108,
            }
        },
    )

class EventOut(BaseModel):
    id: int
    vehicle_id: int
    ecu_id: int | None
    signal_id: int | None
    event_type: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

class EventBatchCreate(BaseModel):
    events: list[EventCreate] = Field(min_length=1, max_length=500)

class EventBatchRejected(BaseModel):
    index: int
    status_code: int
    error: str
    message: str

class EventBatchOut(BaseModel):
    accepted_count: int
    rejected_count: int
    events: list[EventOut]
    rejected: list[EventBatchRejected]

class TelemetrySummaryOut(BaseModel):
    vehicle_id: int
    ecu_count: int
    event_count: int
    last_event_at: datetime | None
    event_counts_by_type: dict[str, int]
