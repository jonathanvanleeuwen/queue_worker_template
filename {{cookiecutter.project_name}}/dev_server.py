"""
Development server for local testing.

1. Start a local Redis instance first:
       docker run -d -p 6379:6379 redis:7-alpine

2. Install the project in editable mode (required for task imports):
       uv pip install -e ".[dev]"

3. Run this script to start the API:
       python dev_server.py

4. In a separate terminal, start the worker to process jobs:
       python dev_worker.py

   Run the worker command again in additional terminals to scale up.
"""

import os

import uvicorn

# Override Redis host for local development
os.environ["REDIS_HOST"] = "localhost"

from {{cookiecutter.project_name}}.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("Queue Worker Development Server")
    print("=" * 60)
    print("\nMake sure Redis is running locally:")
    print("  docker run -d -p 6379:6379 redis:7-alpine")
    print("\nAPI will be available at:")
    print("  http://127.0.0.1:8000")
    print("  http://127.0.0.1:8000/docs (Swagger UI)")
    print("\nDefault API Key: test")
    print("\nTo process enqueued jobs, start the worker in a separate terminal:")
    print("  python dev_worker.py")
    print("=" * 60)
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
