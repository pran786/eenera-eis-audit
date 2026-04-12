"""
/analyze, /status, /report API routes.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from app.models.schemas import (
    ErrorResponse,
    JobStatus,
    ReportResponse,
    StatusResponse,
    UploadResponse,
)
from app.services.audit_service import create_job, get_job, run_analysis
from app.utils.file_utils import FileValidationError

router = APIRouter(tags=["Audit"])


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a document for workflow audit",
    responses={
        400: {"model": ErrorResponse, "description": "Validation failure"},
        422: {"model": ErrorResponse, "description": "Unprocessable entity"},
    },
)
async def analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or DOCX document to audit."),
    hourly_rate: Optional[float] = Form(
        default=None,
        ge=0,
        description="Optional hourly billable rate (USD).",
    ),
) -> UploadResponse:
    """
    Accept a document upload, start an audit job in the background,
    and return a ``job_id`` immediately.
    """

    try:
        job = await create_job(file, hourly_rate=hourly_rate)
    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail,
        ) from exc

    # Kick off the (stub) analysis in the background
    background_tasks.add_task(run_analysis, job.job_id)

    return UploadResponse(
        job_id=job.job_id,
        filename=job.filename,
        status=job.status,  # will be UPLOADED
        created_at=job.created_at,
    )


# ---------------------------------------------------------------------------
# GET /status/{job_id}
# ---------------------------------------------------------------------------

@router.get(
    "/status/{job_id}",
    response_model=StatusResponse,
    summary="Check the status of an audit job",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
async def get_status(job_id: str) -> StatusResponse:
    """Return the current processing status for the given *job_id*."""

    job = get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    return StatusResponse(**job.to_status_dict())


# ---------------------------------------------------------------------------
# GET /report/{job_id}
# ---------------------------------------------------------------------------

@router.get(
    "/report/{job_id}",
    response_model=ReportResponse,
    summary="Retrieve the full audit report",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        409: {"model": ErrorResponse, "description": "Job not yet complete"},
    },
)
async def get_report(job_id: str) -> ReportResponse:
    """
    Return the full audit report once the job has completed.

    Returns **409 Conflict** if the job is still processing.
    """

    job = get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    if job.status == JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Job '{job_id}' failed: {job.error}",
        )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Job '{job_id}' is not yet complete "
                f"(current status: {job.status.value})."
            ),
        )

    return ReportResponse(**job.to_report_dict())
