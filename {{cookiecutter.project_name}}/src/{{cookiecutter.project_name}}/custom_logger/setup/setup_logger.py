import atexit
import json
import logging.config
import logging.handlers
import os
import sys
from pathlib import Path

from {{cookiecutter.project_name}}.settings import get_settings


def load_config() -> dict:
    config_file = Path(Path(__file__).parent.parent, "config/config.json")
    with open(config_file) as f_in:
        return json.load(f_in)


def setup_logging() -> None:
    config = load_config()
    settings = get_settings()

    # Apply log levels from settings
    config["handlers"]["stderr"]["level"] = settings.log_level_console
    config["handlers"]["file_json"]["level"] = settings.log_level_file

    # Disable file logging when running tests
    is_testing = (
        os.getenv("PYTEST_CURRENT_TEST") is not None
        or "pytest" in sys.modules
        or any("pytest" in arg for arg in sys.argv)
    )

    if is_testing:
        # Remove file_json from queue_handler's handlers
        if "queue_handler" in config["handlers"]:
            handlers = config["handlers"]["queue_handler"].get("handlers", [])
            if "file_json" in handlers:
                handlers.remove("file_json")
    else:
        # Only create log directory when not in test mode
        log_file = Path(config["handlers"]["file_json"]["filename"])
        logs_dir = Path(log_file.parent)
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
