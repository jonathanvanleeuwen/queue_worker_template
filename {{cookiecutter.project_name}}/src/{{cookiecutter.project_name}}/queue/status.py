import logging
from typing import Any

from rq.job import Job, JobStatus

from {{cookiecutter.project_name}}.queue.connection import get_redis_connection

logger = logging.getLogger(__name__)


def get_job_status(job_id: str) -> dict[str, Any]:
    """
    Get the current status of a job.

    Args:
        job_id: The unique job identifier

    Returns:
        Dictionary containing job status information
    """
    connection = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=connection)
    except Exception as e:
        logger.error("Failed to fetch job %s: %s", job_id, e)
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": f"Job not found: {str(e)}",
        }

    status_info = {
        "job_id": job.id,
        "status": job.get_status(),
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
    }

    # Add progress information if available
    if hasattr(job, "meta") and job.meta:
        status_info["meta"] = job.meta

    # Add position in queue if job is queued
    if job.get_status() == JobStatus.QUEUED:
        try:
            position = job.get_position()
            if position is not None:
                status_info["position"] = position
        except Exception:
            pass

    return status_info


def get_job_result(job_id: str) -> dict[str, Any]:
    """
    Get the result of a completed job or error information.

    Args:
        job_id: The unique job identifier

    Returns:
        Dictionary containing job result or error information
    """
    connection = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=connection)
    except Exception as e:
        logger.error("Failed to fetch job %s: %s", job_id, e)
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": f"Job not found: {str(e)}",
        }

    result_info = {
        "job_id": job.id,
        "status": job.get_status(),
    }

    # Add result if job is finished
    if job.is_finished:
        result_info["result"] = job.result
        result_info["finished_at"] = job.ended_at.isoformat() if job.ended_at else None

    # Add error information if job failed
    elif job.is_failed:
        result_info["error"] = str(job.exc_info) if job.exc_info else "Unknown error"
        result_info["failed_at"] = job.ended_at.isoformat() if job.ended_at else None

    # Add meta information
    if hasattr(job, "meta") and job.meta:
        result_info["meta"] = job.meta

    return result_info


def cancel_job(job_id: str) -> dict[str, Any]:
    """
    Cancel a job if it's still queued or running.

    Args:
        job_id: The unique job identifier

    Returns:
        Dictionary with cancellation status
    """
    connection = get_redis_connection()

    try:
        job = Job.fetch(job_id, connection=connection)
    except Exception as e:
        logger.error("Failed to fetch job %s: %s", job_id, e)
        return {
            "job_id": job_id,
            "success": False,
            "error": f"Job not found: {str(e)}",
        }

    try:
        if job.get_status() in [JobStatus.QUEUED, JobStatus.STARTED]:
            job.cancel()
            logger.info("Cancelled job %s", job_id)
            return {
                "job_id": job_id,
                "success": True,
                "message": "Job cancelled successfully",
            }
        else:
            return {
                "job_id": job_id,
                "success": False,
                "message": f"Job cannot be cancelled (status: {job.get_status()})",
            }
    except Exception as e:
        logger.error("Failed to cancel job %s: %s", job_id, e)
        return {
            "job_id": job_id,
            "success": False,
            "error": f"Failed to cancel job: {str(e)}",
        }
