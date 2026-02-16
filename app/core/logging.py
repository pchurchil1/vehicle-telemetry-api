import logging
import sys
from pythonjsonlogger.json import JsonFormatter

def configure_logging(log_level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root.handlers = [handler]