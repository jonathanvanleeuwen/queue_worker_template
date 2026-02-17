#!/bin/sh
echo "Starting RQ Worker..."
echo "Redis: ${REDIS_HOST:-redis}:${REDIS_PORT:-6379}/${REDIS_DB:-0}"
echo "Queues: ${QUEUE_NAMES:-default}"

# Build Redis URL
if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_URL="redis://:${REDIS_PASSWORD}@${REDIS_HOST:-redis}:${REDIS_PORT:-6379}/${REDIS_DB:-0}"
else
    REDIS_URL="redis://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}/${REDIS_DB:-0}"
fi

echo "Redis URL: ${REDIS_URL}"

# Start RQ worker with scheduler support
# The worker will process jobs from the specified queues
exec rq worker \
    --with-scheduler \
    --url "$REDIS_URL" \
    --worker-class rq.Worker \
    --name "worker-$(hostname)-$$" \
    --path /opt/app-root/src \
    ${QUEUE_NAMES:-default}
