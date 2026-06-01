from app.core.config import settings
from app.core.logging import configure_logging
from app.services.ingestion_worker import IngestionWorker


def main() -> None:
    configure_logging(settings.log_level)
    IngestionWorker().run_forever()


if __name__ == "__main__":
    main()
