from sqlalchemy.orm import Session

from app.models.ingestion_job import IngestionJob
from app.schemas.ingestion import IngestionJobCreate


class IngestionJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: IngestionJobCreate) -> IngestionJob:
        job = IngestionJob(status="queued", payload=payload.model_dump(mode="json"))
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> IngestionJob | None:
        return self.db.get(IngestionJob, job_id)

    def get_next_queued(self) -> IngestionJob | None:
        return (
            self.db.query(IngestionJob)
            .filter(IngestionJob.status == "queued")
            .order_by(IngestionJob.id.asc())
            .with_for_update(skip_locked=True)
            .first()
        )

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
