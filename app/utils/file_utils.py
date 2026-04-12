"""
File-handling utilities — validation, saving, and cleanup.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import UploadFile

from app.models.schemas import AllowedFileType

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS: dict[str, str] = {
    ".pdf": AllowedFileType.PDF.value,
    ".docx": AllowedFileType.DOCX.value,
}

ALLOWED_MIME_TYPES: set[str] = {t.value for t in AllowedFileType}

MAX_FILE_SIZE_MB: int = 50  # reject files larger than this
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_upload_dir() -> Path:
    """Create the uploads directory if it doesn't already exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def _get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class FileValidationError(Exception):
    """Raised when an uploaded file fails validation."""

    def __init__(self, detail: str, error_code: str = "INVALID_FILE") -> None:
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


async def validate_upload(file: UploadFile) -> None:
    """
    Validate an uploaded file against business rules.

    Raises ``FileValidationError`` on failure.
    """

    # 1. Filename must be present
    if not file.filename:
        raise FileValidationError(
            "Filename is missing from the upload.",
            error_code="MISSING_FILENAME",
        )

    # 2. Extension check
    ext = _get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type '{ext}'. Only PDF and DOCX files are accepted.",
            error_code="UNSUPPORTED_TYPE",
        )

    # 3. MIME type check (belt-and-suspenders)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        # Some clients send generic types — fall back to extension check
        pass  # already validated via extension above

    # 4. Empty-file check — read a small chunk and seek back
    first_chunk = await file.read(1)
    if not first_chunk:
        raise FileValidationError(
            "The uploaded file is empty.",
            error_code="EMPTY_FILE",
        )
    await file.seek(0)

    # 5. Size check — use the underlying file object for whence-based seek
    file.file.seek(0, 2)  # seek to end
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds the {MAX_FILE_SIZE_MB} MB size limit.",
            error_code="FILE_TOO_LARGE",
        )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

async def save_upload(file: UploadFile, job_id: Optional[str] = None) -> Path:
    """
    Save *file* to disk under a unique name and return its path.

    The file is stored inside ``UPLOAD_DIR`` with the pattern
    ``<job_id>_<original_filename>``.
    """
    ensure_upload_dir()

    if job_id is None:
        job_id = uuid.uuid4().hex

    safe_name = f"{job_id}_{file.filename}"
    dest = UPLOAD_DIR / safe_name

    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 64):  # 64 KB chunks
            await out.write(chunk)

    return dest


def remove_file(path: Path | str) -> None:
    """Silently remove a file if it exists."""
    try:
        os.remove(path)
    except OSError:
        pass
