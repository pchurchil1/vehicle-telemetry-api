from queue import Queue
from threading import Lock, Thread

from app.core.db import SessionLocal
from app.repositories.ingestion_repo import IngestionJobRepository
from app.schemas.event import EventBatchCreate
from app.services.event_service import EventService


class IngestionWorker:
    def __init__(self):
        self.queue: Queue[tuple[int, EventBatchCreate]] = Queue()
        self._thread: Thread | None = None
        self._lock = Lock()

    def start(self) -> None:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._thread = Thread(target=self._run, name="telemetry-ingestion-worker", daemon=True)
            self._thread.start()

    def enqueue(self, job_id: int, payload: EventBatchCreate) -> None:
        self.start()
        self.queue.put((job_id, payload))

    def _run(self) -> None:
        while True:
            job_id, payload = self.queue.get()
            db = SessionLocal()
            try:
                jobs = IngestionJobRepository(db)
                job = jobs.get_by_id(job_id)
                if job is None:
                    continue
                jobs.update_status(job, "processing")
                result = EventService(db).create_events_batch(payload)
                jobs.update_status(
                    job,
                    "completed",
                    accepted_count=result.accepted_count,
                    rejected_count=result.rejected_count,
                )
            except Exception as exc:
                db.rollback()
                job = IngestionJobRepository(db).get_by_id(job_id)
                if job is not None:
                    IngestionJobRepository(db).update_status(job, "failed", error_message=str(exc))
            finally:
                db.close()
                self.queue.task_done()


ingestion_worker = IngestionWorker()
