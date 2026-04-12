"""
In-memory job store.

Provides a thread-safe singleton store for audit jobs.  This will be
replaced by a proper database layer later — the interface is kept
intentionally simple to make that migration painless.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any, Optional

from app.models.schemas import JobStatus


class Job:
    """Represents a single audit job and its metadata."""

    __slots__ = (
        "job_id",
        "filename",
        "file_path",
        "status",
        "hourly_rate",
        "created_at",
        "updated_at",
        "completed_at",
        "report",
        "error",
        "extracted_text_length",
        "chunks",
        "chunk_count",
    )

    def __init__(
        self,
        job_id: str,
        filename: str,
        file_path: str,
        hourly_rate: Optional[float] = None,
    ) -> None:
        self.job_id = job_id
        self.filename = filename
        self.file_path = file_path
        self.status: JobStatus = JobStatus.UPLOADED
        self.hourly_rate = hourly_rate
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = self.created_at
        self.completed_at: Optional[datetime] = None
        self.report: Optional[dict[str, Any]] = None
        self.error: Optional[str] = None
        self.extracted_text_length: int = 0
        self.chunks: list[str] = []
        self.chunk_count: int = 0

    # -- Convenience mutators ------------------------------------------------

    def mark_uploaded(self) -> None:
        self.status = JobStatus.UPLOADED
        self.updated_at = datetime.utcnow()

    def mark_processing(self) -> None:
        self.status = JobStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, report: dict[str, Any]) -> None:
        self.status = JobStatus.COMPLETED
        self.report = report
        self.completed_at = datetime.utcnow()
        self.updated_at = self.completed_at

    def mark_failed(self, reason: str) -> None:
        self.status = JobStatus.FAILED
        self.error = reason
        self.updated_at = datetime.utcnow()

    # -- Serialisation helpers -----------------------------------------------

    def to_status_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "filename": self.filename,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "hourly_rate": self.hourly_rate,
            "extracted_text_length": self.extracted_text_length,
            "chunk_count": self.chunk_count,
            "error": self.error,
        }

    def to_report_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "filename": self.filename,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "hourly_rate": self.hourly_rate,
            "extracted_text_length": self.extracted_text_length,
            "chunk_count": self.chunk_count,
            "report": self.report,
            "error": self.error,
        }


class JobStore:
    """Thread-safe in-memory job registry."""

    _instance: Optional["JobStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "JobStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._jobs: dict[str, Job] = {}
            return cls._instance

    # -- Public API ----------------------------------------------------------

    def add(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def exists(self, job_id: str) -> bool:
        return job_id in self._jobs

    def all_jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def remove(self, job_id: str) -> bool:
        with self._lock:
            return self._jobs.pop(job_id, None) is not None

    def clear(self) -> None:
        """Reset store — useful for tests."""
        with self._lock:
            self._jobs.clear()
