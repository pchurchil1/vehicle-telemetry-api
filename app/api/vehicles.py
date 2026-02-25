from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.vehicle import VehicleCreate, VehicleOut
from app.services.vehicle_service import VehicleService

router = APIRouter()

@router.post("/vehicles", response_model=VehicleOut, status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    return VehicleService(db).create_vehicle(payload)

@router.get("/vehicles/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return VehicleService(db).get_vehicle(vehicle_id)

@router.get("/vehicles", response_model=list[VehicleOut])
def list_vehicles(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return VehicleService(db).list_vehicles(limit=limit, offset=offset)