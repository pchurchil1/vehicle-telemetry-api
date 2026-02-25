from pydantic import BaseModel, Field

class VehicleCreate(BaseModel):
    vin: str = Field(min_length=17, max_length=17)
    make: str
    model: str
    year: int = Field(ge=1980, le=2100)

class VehicleOut(BaseModel):
    id: int
    vin: str
    make: str
    model: str
    year: int

    model_config = {"from_attributes": True}