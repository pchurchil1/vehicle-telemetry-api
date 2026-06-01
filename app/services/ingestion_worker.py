import time

from app.core.db import SessionLocal
from app.repositories.ingestion_repo import IngestionJobRepository
from app.schemas.event import EventBatchCreate
from app.services.event_service import EventService


class IngestionWorker:
    def __init__(self, poll_interval_seconds: float = 1.0):
        self.poll_interval_seconds = poll_interval_seconds

    def process_next_job(self) -> bool:
        db = SessionLocal()
        try:
            jobs = IngestionJobRepository(db)
            job = jobs.get_next_queued()
            if job is None:
                return False

            jobs.update_status(job, "processing")
            payload = EventBatchCreate.model_validate(job.payload)
            result = EventService(db).create_events_batch(payload)
            jobs.update_status(
                job,
                "completed",
                accepted_count=result.accepted_count,
                rejected_count=result.rejected_count,
            )
            return True
        except Exception as exc:
            db.rollback()
            if "job" in locals() and job is not None:
                IngestionJobRepository(db).update_status(job, "failed", error_message=str(exc))
                return True
            return False
        finally:
            db.close()

    def run_forever(self) -> None:
        while True:
            processed = self.process_next_job()
            if not processed:
                time.sleep(self.poll_interval_seconds)
