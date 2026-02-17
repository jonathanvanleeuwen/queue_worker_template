#!/bin/sh
echo "Installed packages:"
uv pip list

echo "Starting Queue Worker API..."
echo "Using port: ${PORT:-8000}"
exec uvicorn $UVICORN_ENTRYPOINT --proxy-headers --forwarded-allow-ips "*" --host 0.0.0.0 --port ${PORT:-8000}
