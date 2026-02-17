import logging
from collections.abc import Callable
from typing import Any

from rq import Queue
from rq.job import Job

from {{cookiecutter.project_name}}.queue.connection import get_redis_connection
from {{cookiecutter.project_name}}.settings import get_settings

logger = logging.getLogger(__name__)


def get_queue(queue_name: str | None = None) -> Queue:
    """
    Get RQ Queue instance for the specified queue name.

    Args:
        queue_name: Name of the queue. If None, uses default queue from settings.

    Returns:
        Queue instance
    """
    settings = get_settings()
    if queue_name is None:
        queue_name = settings.default_queue

    connection = get_redis_connection()
    return Queue(name=queue_name, connection=connection)


def enqueue_job(
    task_func: Callable,
    *args: Any,
    queue_name: str | None = None,
    job_timeout: int | None = None,
    result_ttl: int | None = None,
    **kwargs: Any,
) -> Job:
    """
    Enqueue a job to be processed by RQ workers.

    Args:
        task_func: The function to be executed by the worker
        *args: Positional arguments to pass to the task function
        queue_name: Name of the queue (default: from settings)
        job_timeout: Job execution timeout in seconds (default: from settings)
        result_ttl: Time to keep result in Redis in seconds (default: from settings)
        **kwargs: Keyword arguments to pass to the task function

    Returns:
        Job instance with job ID and metadata
    """
    settings = get_settings()
    queue = get_queue(queue_name)

    if job_timeout is None:
        job_timeout = settings.job_timeout
    if result_ttl is None:
        result_ttl = settings.result_ttl

    job = queue.enqueue(
        task_func,
        *args,
        job_timeout=job_timeout,
        result_ttl=result_ttl,
        **kwargs,
    )

    logger.info(
        "Enqueued job %s to queue '%s' (task: %s)",
        job.id,
        queue_name or settings.default_queue,
        task_func.__name__,
    )

    return job
