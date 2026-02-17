import inspect
import logging

from fastapi import APIRouter, HTTPException, Request, status

from {{cookiecutter.project_name}}.models.jobs import (
    AvailableTasksResponse,
    EnqueueRequest,
    EnqueueResponse,
    JobCancelResponse,
    JobResultResponse,
    JobStatusResponse,
    QueueStatsResponse,
)
from {{cookiecutter.project_name}}.queue.enqueue import enqueue_job, get_queue
from {{cookiecutter.project_name}}.queue.status import cancel_job, get_job_result, get_job_status
from {{cookiecutter.project_name}}.workers.tasks import long_running_task, process_csv, transform_data

logger = logging.getLogger(__name__)

jobs_router = APIRouter(tags=["jobs"], prefix="/api/jobs")

# Registry of available tasks
TASK_REGISTRY = {
    "transform_data": transform_data,
    "process_csv": process_csv,
    "long_running_task": long_running_task,
}


@jobs_router.post("/enqueue", status_code=status.HTTP_201_CREATED)
def enqueue_job_endpoint(
    request_data: EnqueueRequest, request: Request
) -> EnqueueResponse:
    """
    Enqueue a new job for processing.

    The job will be added to the specified queue and processed by available workers.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.info(
        "User %s enqueueing job: task=%s, queue=%s",
        user,
        request_data.task_name,
        request_data.queue,
    )

    # Validate task exists
    if request_data.task_name not in TASK_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task: {request_data.task_name}. Available tasks: {list(TASK_REGISTRY.keys())}",
        )

    task_func = TASK_REGISTRY[request_data.task_name]

    try:
        job = enqueue_job(
            task_func,
            queue_name=request_data.queue,
            job_timeout=request_data.timeout,
            result_ttl=request_data.result_ttl,
            **request_data.task_args,
        )

        return EnqueueResponse(
            job_id=job.id,
            queue=request_data.queue,
            task_name=request_data.task_name,
            status=job.get_status(),
            enqueued_at=job.enqueued_at.isoformat() if job.enqueued_at else None,
        )

    except Exception as e:
        logger.error("Failed to enqueue job: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue job: {str(e)}",
        ) from e


@jobs_router.get("/{job_id}/status", status_code=status.HTTP_200_OK)
def get_job_status_endpoint(job_id: str, request: Request) -> JobStatusResponse:
    """
    Get the current status of a job.

    Returns information about the job's current state, timestamps, and position in queue.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.debug("User %s requesting status for job %s", user, job_id)

    status_info = get_job_status(job_id)

    if status_info.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=status_info.get("error", "Job not found"),
        )

    return JobStatusResponse(**status_info)


@jobs_router.get("/{job_id}/result", status_code=status.HTTP_200_OK)
def get_job_result_endpoint(job_id: str, request: Request) -> JobResultResponse:
    """
    Get the result of a completed job.

    Returns the job result if completed, or error information if failed.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.debug("User %s requesting result for job %s", user, job_id)

    result_info = get_job_result(job_id)

    if result_info.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result_info.get("error", "Job not found"),
        )

    return JobResultResponse(**result_info)


@jobs_router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def cancel_job_endpoint(job_id: str, request: Request) -> JobCancelResponse:
    """
    Cancel a queued or running job.

    Only jobs that are queued or currently running can be cancelled.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.info("User %s requesting cancellation for job %s", user, job_id)

    cancel_result = cancel_job(job_id)

    if not cancel_result.get("success") and cancel_result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=cancel_result.get("error", "Job not found"),
        )

    return JobCancelResponse(**cancel_result)


@jobs_router.get("/tasks/available", status_code=status.HTTP_200_OK)
def get_available_tasks(request: Request) -> AvailableTasksResponse:
    """
    Get list of available task functions.

    Returns all tasks that can be enqueued for processing.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.debug("User %s requesting available tasks", user)

    tasks = []
    for name, func in TASK_REGISTRY.items():
        # Use inspect.getdoc to properly extract
        doc = inspect.getdoc(func)
        description = doc if doc else "No description"
        tasks.append({"name": name, "description": description})

    return AvailableTasksResponse(tasks=tasks, count=len(tasks))


@jobs_router.get("/queues/{queue_name}/stats", status_code=status.HTTP_200_OK)
def get_queue_stats(queue_name: str, request: Request) -> QueueStatsResponse:
    """
    Get statistics for a specific queue.

    Returns the number of jobs and other queue information.
    """
    user_info = request.state.user_info
    user = user_info.get("sub", "unknown")
    logger.debug("User %s requesting stats for queue %s", user, queue_name)

    try:
        queue = get_queue(queue_name)
        job_count = len(queue)

        # Get oldest job timestamp if available
        oldest_job_timestamp = None
        jobs = queue.jobs[:1]  # Get first job
        if jobs:
            oldest_job_timestamp = (
                jobs[0].created_at.isoformat() if jobs[0].created_at else None
            )

        return QueueStatsResponse(
            queue_name=queue_name,
            job_count=job_count,
            oldest_job_timestamp=oldest_job_timestamp,
        )

    except Exception as e:
        logger.error("Failed to get queue stats: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get queue stats: {str(e)}",
        ) from e
