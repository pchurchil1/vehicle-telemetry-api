import os
import tempfile
from pathlib import Path


TEST_DB_PATH = Path(tempfile.gettempdir()) / "vehicle_telemetry_api_test.db"
RUN_POSTGRES_TESTS = os.environ.get("RUN_POSTGRES_TESTS") == "1"

if not RUN_POSTGRES_TESTS and TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

if not RUN_POSTGRES_TESTS:
    test_database_url = f"sqlite:///{TEST_DB_PATH}"
    os.environ["DATABASE_URL"] = test_database_url
    os.environ["DATABASE_URL_TEST"] = test_database_url
os.environ["ENVIRONMENT"] = "test"

from app.core.db import Base
from app.models.ecu import Ecu
from app.models.event import Event
from app.models.ingestion_job import IngestionJob
from app.models.signal import Signal
from app.models.user import User
from app.models.vehicle import Vehicle
from app.core.db import engine


def pytest_sessionstart(session):
    Base.metadata.create_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    Base.metadata.drop_all(bind=engine)
    if not RUN_POSTGRES_TESTS and TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
