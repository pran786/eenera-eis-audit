"""
Pydantic schemas for request/response models.
Defines the data contracts for the Eenera audit API.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JobStatus(str, Enum):
    """Lifecycle states of an audit job."""

    UPLOADED = "uploaded"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AllowedFileType(str, Enum):
    """Accepted document MIME types."""

    PDF = "application/pdf"
    DOCX = (
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document"
    )


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------

class AnalyzeParams(BaseModel):
    """Optional parameters that accompany the file upload."""

    hourly_rate: Optional[float] = Field(
        default=None,
        ge=0,
        description="Hourly billable rate (USD) used in cost calculations.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    """Returned immediately after a successful file upload."""

    job_id: str = Field(..., description="Unique identifier for this audit job.")
    filename: str = Field(..., description="Original uploaded filename.")
    status: JobStatus = Field(default=JobStatus.PENDING)
    message: str = Field(
        default="File uploaded successfully. Processing will begin shortly.",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "job_id": "a12b34c5-d678-90ef-gh12-i34567890jkl",
                "filename": "workflow.pdf",
                "status": "pending",
                "message": "File uploaded successfully. Processing will begin shortly.",
                "created_at": "2026-04-10T12:00:00",
            }
        ]
    }}


class StatusResponse(BaseModel):
    """Current status of a specific audit job."""

    job_id: str
    status: JobStatus
    filename: str
    created_at: datetime
    updated_at: datetime
    hourly_rate: Optional[float] = None
    extracted_text_length: int = Field(
        default=0,
        description="Character count of extracted text (debug info).",
    )
    chunk_count: int = Field(
        default=0,
        description="Number of text chunks produced by the pipeline.",
    )
    error: Optional[str] = None


class ReportResponse(BaseModel):
    """Full audit report for a completed job."""

    job_id: str
    status: JobStatus
    filename: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    hourly_rate: Optional[float] = None
    extracted_text_length: int = Field(
        default=0,
        description="Character count of extracted text (debug info).",
    )
    chunk_count: int = Field(
        default=0,
        description="Number of text chunks produced by the pipeline.",
    )
    report: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardised error payload."""

    detail: str
    error_code: Optional[str] = None
