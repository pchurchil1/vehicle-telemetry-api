from pydantic import BaseModel, Field

class VehicleCreate(BaseModel):
    vin: str = Field(min_length=17, max_length=17, json_schema_extra={"example": "1FTFW1RG0PFA12345"})
    make: str = Field(min_length=1, max_length=50, json_schema_extra={"example": "Ford"})
    model: str = Field(min_length=1, max_length=50, json_schema_extra={"example": "F-150"})
    year: int = Field(ge=1980, le=2100)

class VehicleUpdate(BaseModel):
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    make: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1980, le=2100)

class VehicleOut(BaseModel):
    id: int
    vin: str
    make: str
    model: str
    year: int

    model_config = {"from_attributes": True}
