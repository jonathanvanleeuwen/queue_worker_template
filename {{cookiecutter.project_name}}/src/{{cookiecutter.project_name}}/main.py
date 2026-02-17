import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lib_auth.auth.authentication import create_auth

from {{cookiecutter.project_name}}.custom_logger.setup.setup_logger import setup_logging
from {{cookiecutter.project_name}}.queue.connection import get_redis_connection
from {{cookiecutter.project_name}}.routers.jobs import jobs_router
from {{cookiecutter.project_name}}.settings import get_settings

setup_logging()
logger = logging.getLogger(__name__)

# Create auth dependency at module level (not a factory)
# This will use settings available at import time
settings = get_settings()
auth_dependency = create_auth(
    api_keys=settings.api_keys,
    oauth_secret_key=settings.oauth_secret_key,
    allowed_roles=["admin", "user"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Queue Worker API")
    try:
        # Test Redis connection
        redis_conn = get_redis_connection()
        redis_conn.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error("Failed to connect to Redis: %s", e)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Queue Worker API")


app = FastAPI(
    title="{{cookiecutter.project_name}}",
    version="0.1.0",
    description="{{cookiecutter.app_description}}",
    lifespan=lifespan,
)

# Get settings for middleware
_settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    """Root endpoint with API information."""
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "description": settings.description,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint.

    Verifies that the API and Redis connection are working.
    """
    try:
        redis_conn = get_redis_connection()
        redis_conn.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error("Redis health check failed: %s", e)
        redis_status = f"unhealthy: {str(e)}"
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": redis_status,
            },
        )

    return {
        "status": "healthy",
        "redis": redis_status,
    }


# Add protected jobs router with authentication
app.include_router(
    jobs_router,
    dependencies=[Depends(auth_dependency)],
)
