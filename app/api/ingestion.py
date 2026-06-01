from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER, require_roles
from app.schemas.ingestion import IngestionJobCreate, IngestionJobOut
from app.services.ingestion_service import IngestionService


router = APIRouter()


@router.post(
    "/ingestion/events",
    response_model=IngestionJobOut,
    status_code=202,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER))],
)
def enqueue_event_ingestion(payload: IngestionJobCreate, db: Session = Depends(get_db)):
    return IngestionService(db).enqueue_events(payload)


@router.get(
    "/ingestion/jobs/{job_id}",
    response_model=IngestionJobOut,
    dependencies=[Depends(require_roles(ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER))],
)
def get_ingestion_job(job_id: int, db: Session = Depends(get_db)):
    return IngestionService(db).get_job(job_id)
