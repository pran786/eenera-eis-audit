"""
Audit orchestration service.

Coordinates the full lifecycle of an audit job:
upload → validate → persist → (future) analyse → report.

The actual AI analysis is **stubbed** here.  Swap in your real
analysis pipeline once the infrastructure is wired up.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.models.job import Job, JobStore
from app.models.schemas import JobStatus
from app.services.analysis_engine import analyze_inefficiencies
from app.services.extractor import ExtractionError, extract_text
from app.services.pipeline import process_document
from app.services.report_generator import generate_report
from app.services.workflow_analyzer import analyze_workflow
from app.utils.file_utils import (
    remove_file,
    save_upload,
    validate_upload,
)

# Singleton store
_store = JobStore()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def create_job(
    file: UploadFile,
    hourly_rate: Optional[float] = None,
) -> Job:
    """
    Validate and persist *file*, create a ``Job`` entry, and return it.

    Raises ``FileValidationError`` if the upload is invalid.
    """

    # Validate before anything else
    await validate_upload(file)

    job_id = uuid.uuid4().hex
    file_path = await save_upload(file, job_id=job_id)

    job = Job(
        job_id=job_id,
        filename=file.filename or "unknown",
        file_path=str(file_path),
        hourly_rate=hourly_rate,
    )
    _store.add(job)

    return job


def get_job(job_id: str) -> Optional[Job]:
    """Return a job by ID or ``None``."""
    return _store.get(job_id)


def get_all_jobs() -> list[Job]:
    """Return every known job (most-recent first)."""
    jobs = _store.all_jobs()
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    return jobs


# ---------------------------------------------------------------------------
# Analysis pipeline
# ---------------------------------------------------------------------------

async def run_analysis(job_id: str) -> None:
    """
    Run the analysis pipeline for *job_id*:

    1. Extract text from the uploaded document.
    2. (Future) Send it through the AI model for workflow analysis.
    3. Build a structured report.
    4. Mark the job as completed.
    """

    job = _store.get(job_id)
    if job is None:
        return

    job.mark_processing()

    try:
        # ── Step 1: Text extraction ─────────────────────────────────
        extracted_text = extract_text(job.file_path)
        job.extracted_text_length = len(extracted_text)

        # ── Step 2: Chunking via pipeline ───────────────────────────
        chunks = process_document(extracted_text)
        job.chunks = chunks
        job.chunk_count = len(chunks)

        # ── Step 3: LLM-powered workflow extraction ────────────────
        workflow = await analyze_workflow(chunks)

        # ── Step 4: Inefficiency & cost analysis ───────────────────
        cost_analysis = await analyze_inefficiencies(
            workflow_data=workflow,
            hourly_rate=job.hourly_rate,
        )

        # ── Step 5: Build report ────────────────────────────────────
        report = {
            "summary": "Workflow audit analysis complete.",
            "extracted_text_length": job.extracted_text_length,
            "chunk_count": job.chunk_count,
            "chunk_sizes": [len(c) for c in chunks],
            # Workflow extraction results
            "workflow_steps": workflow.get("workflow_steps", []),
            "manual_tasks": workflow.get("manual_tasks", []),
            "repeated_tasks": workflow.get("repeated_tasks", []),
            "bottlenecks": workflow.get("bottlenecks", []),
            "delays": workflow.get("delays", []),
            "total_steps_identified": len(workflow.get("workflow_steps", [])),
            "redundant_steps": len(workflow.get("repeated_tasks", [])),
            "automation_candidates": len(workflow.get("manual_tasks", [])),
            # Inefficiency & cost analysis
            "inefficiencies": cost_analysis.get("inefficiencies", []),
            "time_loss_hours_per_day": cost_analysis.get("time_loss_hours_per_day", 0.0),
            "revenue_leakage": cost_analysis.get("revenue_leakage", []),
            "cost_analysis": cost_analysis.get("cost_analysis", {}),
            "hourly_rate": cost_analysis.get("hourly_rate", 15.0),
            "estimated_time_savings_hours": cost_analysis.get("time_loss_hours_per_day", 0.0),
            "estimated_cost_savings": cost_analysis.get("cost_analysis", {}).get("monthly_cost", 0.0),
            "recommendations": [],
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        # ── Step 6: Generate markdown report ───────────────────────
        report["markdown_report"] = generate_report(
            workflow_data=workflow,
            cost_data=cost_analysis,
            filename=job.filename,
            job_id=job.job_id,
        )

        job.mark_completed(report)

    except ExtractionError as exc:
        job.mark_failed(f"Text extraction failed: {exc.detail}")

    except Exception as exc:  # noqa: BLE001
        job.mark_failed(str(exc))


def delete_job(job_id: str) -> bool:
    """Remove a job and clean up its uploaded file."""
    job = _store.get(job_id)
    if job is None:
        return False

    remove_file(job.file_path)
    return _store.remove(job_id)
