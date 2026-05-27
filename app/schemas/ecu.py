from pydantic import BaseModel, Field

class EcuCreate(BaseModel):
    vehicle_id: int = Field(json_schema_extra={"example": 1})
    name: str = Field(min_length=1, max_length=80, json_schema_extra={"example": "ECM"})
    supplier: str | None = Field(default=None, max_length=80, json_schema_extra={"example": "Bosch"})

class EcuUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    supplier: str | None = Field(default=None, max_length=80)

class EcuOut(BaseModel):
    id: int
    vehicle_id: int
    name: str
    supplier: str | None

    model_config = {"from_attributes": True}
