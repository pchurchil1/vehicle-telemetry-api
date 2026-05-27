from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.auth import require_api_key
from app.core.db import get_db
from app.schemas.ecu import EcuCreate, EcuOut, EcuUpdate
from app.services.ecu_service import EcuService

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/ecus", response_model=EcuOut, status_code=201)
def create_ecu(payload: EcuCreate, db: Session = Depends(get_db)):
    return EcuService(db).create_ecu(payload)

@router.get("/ecus/{ecu_id}", response_model=EcuOut)
def get_ecu(ecu_id: int, db: Session = Depends(get_db)):
    return EcuService(db).get_ecu(ecu_id)

@router.patch("/ecus/{ecu_id}", response_model=EcuOut)
def update_ecu(ecu_id: int, payload: EcuUpdate, db: Session = Depends(get_db)):
    return EcuService(db).update_ecu(ecu_id, payload)

@router.delete("/ecus/{ecu_id}", status_code=204)
def delete_ecu(ecu_id: int, db: Session = Depends(get_db)):
    EcuService(db).delete_ecu(ecu_id)
    return Response(status_code=204)

@router.get("/vehicles/{vehicle_id}/ecus", response_model=list[EcuOut])
def list_ecus_for_vehicle(
    vehicle_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return EcuService(db).list_ecus_for_vehicle(vehicle_id, limit=limit, offset=offset)
