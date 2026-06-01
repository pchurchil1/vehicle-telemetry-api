from pydantic import BaseModel, Field


class SignalCreate(BaseModel):
    vehicle_id: int
    ecu_id: int | None = None
    name: str = Field(min_length=1, max_length=120, json_schema_extra={"example": "engine_rpm"})
    unit: str | None = Field(default=None, max_length=40, json_schema_extra={"example": "rpm"})
    data_type: str = Field(min_length=1, max_length=40, json_schema_extra={"example": "integer"})
    description: str | None = Field(default=None, max_length=500)


class SignalUpdate(BaseModel):
    ecu_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    unit: str | None = Field(default=None, max_length=40)
    data_type: str | None = Field(default=None, min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=500)


class SignalOut(BaseModel):
    id: int
    vehicle_id: int
    ecu_id: int | None
    name: str
    unit: str | None
    data_type: str
    description: str | None

    model_config = {"from_attributes": True}
