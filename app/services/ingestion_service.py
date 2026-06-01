from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.ingestion_repo import IngestionJobRepository
from app.schemas.ingestion import IngestionJobCreate
from app.services.ingestion_worker import ingestion_worker


class IngestionService:
    def __init__(self, db: Session):
        self.jobs = IngestionJobRepository(db)

    def enqueue_events(self, data: IngestionJobCreate):
        job = self.jobs.create()
        ingestion_worker.enqueue(job.id, data)
        return job

    def get_job(self, job_id: int):
        job = self.jobs.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        return job
