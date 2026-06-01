from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER, require_roles
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate
from app.services.vehicle_service import VehicleService

router = APIRouter()

@router.post(
    "/vehicles",
    response_model=VehicleOut,
    status_code=201,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER))],
)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    return VehicleService(db).create_vehicle(payload)

@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleOut,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER))],
)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return VehicleService(db).get_vehicle(vehicle_id)

@router.patch(
    "/vehicles/{vehicle_id}",
    response_model=VehicleOut,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER))],
)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    return VehicleService(db).update_vehicle(vehicle_id, payload)

@router.delete(
    "/vehicles/{vehicle_id}",
    status_code=204,
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    VehicleService(db).delete_vehicle(vehicle_id)
    return Response(status_code=204)

@router.get(
    "/vehicles",
    response_model=list[VehicleOut],
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER))],
)
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
