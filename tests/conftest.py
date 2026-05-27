import os
import tempfile
from pathlib import Path


TEST_DB_PATH = Path(tempfile.gettempdir()) / "vehicle_telemetry_api_test.db"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

test_database_url = f"sqlite:///{TEST_DB_PATH}"
os.environ["DATABASE_URL"] = test_database_url
os.environ["DATABASE_URL_TEST"] = test_database_url
os.environ["ENVIRONMENT"] = "test"

from app.core.db import Base
from app.models.ecu import Ecu
from app.models.event import Event
from app.models.vehicle import Vehicle
from app.core.db import engine


def pytest_sessionstart(session):
    Base.metadata.create_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
