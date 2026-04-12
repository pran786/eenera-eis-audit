"""
Eenera — AI-Powered Workflow Audit System
==========================================

Application entry-point.  Run with::

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as audit_router
from app.utils.file_utils import ensure_upload_dir


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hook."""
    # Ensure the upload directory exists on boot
    ensure_upload_dir()
    yield
    # Cleanup logic (if needed) goes here


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Eenera — AI Workflow Audit API",
    description=(
        "Upload PDF or DOCX documents describing business workflows. "
        "Eenera analyses them using AI and returns a structured audit "
        "report identifying redundancies, automation candidates, and "
        "estimated cost savings."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(audit_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"], summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "eenera-audit-api"}


@app.get("/", tags=["System"], summary="Root")
async def root() -> dict[str, str]:
    return {
        "service": "Eenera — AI Workflow Audit API",
        "version": "1.0.0",
        "docs": "/docs",
    }
