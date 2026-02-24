"""
Development worker for local testing.

Prerequisite - Redis must be running:
    docker run -d -p 6379:6379 redis:7-alpine

Start the API server in a separate terminal first:
    python dev_server.py

Then run this script in another terminal to process enqueued jobs:
    python dev_worker.py

The worker imports tasks from the installed package, so make sure you have
installed the project in editable mode before running:
    uv pip install -e ".[dev]"

To run multiple workers (for parallel job processing), open additional
terminals and run this script again in each one.

Note: This script uses rq.SimpleWorker instead of rq.Worker because the
standard Worker relies on os.fork(), which is not available on Windows.
SimpleWorker runs jobs in the same process, which is fine for local development.
"""

import os

# Must be set before importing {{cookiecutter.project_name}} to override the default Redis host
os.environ["REDIS_HOST"] = "localhost"

from rq import Queue
from rq.worker import SimpleWorker

from {{cookiecutter.project_name}}.queue.connection import get_redis_connection
from {{cookiecutter.project_name}}.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    queue_names = settings.get_queue_list()
    connection = get_redis_connection()

    print("=" * 60)
    print("Queue Worker Development Worker")
    print("=" * 60)
    print("\nRedis:")
    print(f"  {settings.redis_host}:{settings.redis_port}/{settings.redis_db}")
    print("\nListening on queues:")
    for name in queue_names:
        print(f"  - {name}")
    print("\nImporting tasks from:")
    print("  {{cookiecutter.project_name}}.workers.tasks")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    print()

    queues = [Queue(name=name, connection=connection) for name in queue_names]
    worker = SimpleWorker(queues=queues, connection=connection)
    worker.work(with_scheduler=True)
