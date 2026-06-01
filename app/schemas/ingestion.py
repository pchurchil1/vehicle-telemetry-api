from datetime import datetime

from pydantic import BaseModel

from app.schemas.event import EventBatchCreate


class IngestionJobCreate(EventBatchCreate):
    pass


class IngestionJobOut(BaseModel):
    id: int
    status: str
    accepted_count: int
    rejected_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
