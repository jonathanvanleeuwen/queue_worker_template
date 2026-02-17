import logging
from functools import lru_cache

import redis

from {{cookiecutter.project_name}}.settings import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_redis_connection() -> redis.Redis:
    """
    Get Redis connection instance.
    Uses connection pooling and caching for efficiency.
    """
    settings = get_settings()
    logger.info(
        "Creating Redis connection to %s:%s",
        settings.redis_host,
        settings.redis_port,
    )

    connection = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=False,  # RQ handles encoding
        socket_connect_timeout=5,
        socket_timeout=5,
    )

    # Test connection
    try:
        connection.ping()
        logger.info("Redis connection successful")
    except redis.ConnectionError as e:
        logger.error("Failed to connect to Redis: %s", e)
        raise

    return connection
