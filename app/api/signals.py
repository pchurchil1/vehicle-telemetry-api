from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER, require_roles
from app.schemas.signal import SignalCreate, SignalOut, SignalUpdate
from app.services.signal_service import SignalService


router = APIRouter()


@router.post(
    "/signals",
    response_model=SignalOut,
    status_code=201,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER))],
)
def create_signal(payload: SignalCreate, db: Session = Depends(get_db)):
    return SignalService(db).create_signal(payload)


@router.get(
    "/signals/{signal_id}",
    response_model=SignalOut,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER))],
)
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    return SignalService(db).get_signal(signal_id)


@router.patch(
    "/signals/{signal_id}",
    response_model=SignalOut,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER))],
)
def update_signal(signal_id: int, payload: SignalUpdate, db: Session = Depends(get_db)):
    return SignalService(db).update_signal(signal_id, payload)


@router.delete(
    "/signals/{signal_id}",
    status_code=204,
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)
def delete_signal(signal_id: int, db: Session = Depends(get_db)):
    SignalService(db).delete_signal(signal_id)
    return Response(status_code=204)


@router.get(
    "/vehicles/{vehicle_id}/signals",
    response_model=list[SignalOut],
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER))],
)
def list_signals_for_vehicle(
    vehicle_id: int,
    ecu_id: int | None = Query(None),
    name: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return SignalService(db).list_signals_for_vehicle(
        vehicle_id=vehicle_id,
        ecu_id=ecu_id,
        name=name,
        limit=limit,
        offset=offset,
    )
