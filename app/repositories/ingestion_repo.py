from sqlalchemy.orm import Session

from app.models.ingestion_job import IngestionJob


class IngestionJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self) -> IngestionJob:
        job = IngestionJob(status="queued")
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> IngestionJob | None:
        return self.db.get(IngestionJob, job_id)

    def update_status(
        self,
        job: IngestionJob,
        status: str,
        accepted_count: int | None = None,
        rejected_count: int | None = None,
        error_message: str | None = None,
    ) -> IngestionJob:
        job.status = status
        if accepted_count is not None:
            job.accepted_count = accepted_count
        if rejected_count is not None:
            job.rejected_count = rejected_count
        job.error_message = error_message
        self.db.commit()
        self.db.refresh(job)
        return job
