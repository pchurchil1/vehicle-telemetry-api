from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.ingestion_repo import IngestionJobRepository
from app.schemas.ingestion import IngestionJobCreate


class IngestionService:
    def __init__(self, db: Session):
        self.jobs = IngestionJobRepository(db)

    def enqueue_events(self, data: IngestionJobCreate):
        return self.jobs.create(data)

    def get_job(self, job_id: int):
        job = self.jobs.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Ingestion job not found")
        return job
