from typing import Any

from pydantic import BaseModel, Field


class EnqueueRequest(BaseModel):
    """Request model for enqueueing a new job."""

    task_name: str = Field(
        ...,
        description="Name of the task function to execute",
        examples=["transform_data", "process_csv", "long_running_task"],
    )
    task_args: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the task function",
        examples=[{"data": {"key": "value"}, "operation": "uppercase_keys"}],
    )
    queue: str = Field(
        default="default",
        description="Queue name to enqueue the job to",
        examples=["default", "high", "low"],
    )
    timeout: int = Field(
        default=600,
        description="Job execution timeout in seconds",
        gt=0,
        le=3600,
    )
    result_ttl: int = Field(
        default=3600,
        description="Time to keep result in Redis (seconds)",
        gt=0,
        le=86400,
    )


class EnqueueResponse(BaseModel):
    """Response model after enqueueing a job."""

    job_id: str = Field(..., description="Unique identifier for the job")
    queue: str = Field(..., description="Queue where the job was enqueued")
    task_name: str = Field(..., description="Name of the task function")
    status: str = Field(..., description="Initial status of the job")
    enqueued_at: str | None = Field(None, description="When the job was enqueued")


class JobStatusResponse(BaseModel):
    """Response model for job status queries."""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(
        ...,
        description="Current status (queued, started, finished, failed, cancelled)",
    )
    created_at: str | None = Field(None, description="When the job was created")
    started_at: str | None = Field(None, description="When the job started executing")
    ended_at: str | None = Field(None, description="When the job finished")
    enqueued_at: str | None = Field(None, description="When the job was enqueued")
    position: int | None = Field(
        None, description="Position in queue (if still queued)"
    )
    meta: dict[str, Any] | None = Field(None, description="Job metadata")


class JobResultResponse(BaseModel):
    """Response model for job result queries."""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(..., description="Job status")
    result: Any | None = Field(None, description="Job result if completed")
    error: str | None = Field(None, description="Error message if failed")
    finished_at: str | None = Field(None, description="When the job finished")
    failed_at: str | None = Field(None, description="When the job failed")
    meta: dict[str, Any] | None = Field(None, description="Job metadata")


class JobCancelResponse(BaseModel):
    """Response model for job cancellation."""

    job_id: str = Field(..., description="Unique identifier for the job")
    success: bool = Field(..., description="Whether cancellation was successful")
    message: str | None = Field(None, description="Status message")
    error: str | None = Field(None, description="Error message if failed")


class AvailableTasksResponse(BaseModel):
    """Response model listing available tasks."""

    tasks: list[dict[str, str]] = Field(
        ..., description="List of available task functions with descriptions"
    )
    count: int = Field(..., description="Number of available tasks")


class QueueStatsResponse(BaseModel):
    """Response model for queue statistics."""

    queue_name: str = Field(..., description="Name of the queue")
    job_count: int = Field(..., description="Number of jobs in queue")
    oldest_job_timestamp: str | None = Field(
        None, description="Timestamp of oldest job"
    )
