"""
Development server for local testing.

Start a local Redis instance first:
    docker run -d -p 6379:6379 redis:7-alpine

Or install Redis locally and run:
    redis-server

Then run this script:
    python dev_server.py
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
    print("=" * 60)
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
