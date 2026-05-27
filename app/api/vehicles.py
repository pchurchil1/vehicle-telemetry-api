from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.auth import require_api_key
from app.core.db import get_db
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate
from app.services.vehicle_service import VehicleService

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/vehicles", response_model=VehicleOut, status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    return VehicleService(db).create_vehicle(payload)

@router.get("/vehicles/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return VehicleService(db).get_vehicle(vehicle_id)

@router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    return VehicleService(db).update_vehicle(vehicle_id, payload)

@router.delete("/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    VehicleService(db).delete_vehicle(vehicle_id)
    return Response(status_code=204)

@router.get("/vehicles", response_model=list[VehicleOut])
def list_vehicles(
    make: str | None = Query(None, min_length=1, max_length=50),
    model: str | None = Query(None, min_length=1, max_length=50),
    year: int | None = Query(None, ge=1980, le=2100),
    vin_prefix: str | None = Query(None, min_length=1, max_length=17),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return VehicleService(db).list_vehicles(
        limit=limit,
        offset=offset,
        make=make,
        model=model,
        year=year,
        vin_prefix=vin_prefix,
    )
