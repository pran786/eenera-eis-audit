"""
Document processing pipeline.

Handles text chunking and document processing logic.
Designed to be extended with async processing support.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 100,
) -> list[str]:
    """
    Split *text* into overlapping chunks of approximately *chunk_size*
    characters.

    The function tries to break at sentence boundaries (`. `, `\\n`)
    to avoid cutting mid-sentence.  When no boundary is found within
    the window, it falls back to a hard cut at *chunk_size*.

    Parameters
    ----------
    text : str
        The full document text.
    chunk_size : int
        Target maximum character count per chunk (default 1200).
    overlap : int
        Number of characters to overlap between consecutive chunks
        so context is not lost at boundaries.

    Returns
    -------
    list[str]
        Ordered list of text chunks.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    # Short-circuit if the entire text fits in a single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If we've reached or passed the end, take the rest
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to find a clean break point (sentence boundary)
        segment = text[start:end]
        break_point = _find_break_point(segment)

        if break_point > 0:
            actual_end = start + break_point
        else:
            actual_end = end

        chunk = text[start:actual_end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance with overlap to preserve context
        start = actual_end - overlap
        if start < 0:
            start = 0
        # Prevent infinite loop
        if start >= actual_end:
            start = actual_end

    logger.info(
        "Chunked %d chars into %d chunks (size=%d, overlap=%d)",
        len(text), len(chunks), chunk_size, overlap,
    )

    return chunks


def _find_break_point(segment: str) -> int:
    """
    Find the last natural break point in *segment*.

    Prefers paragraph breaks > sentence-ending periods > newlines.
    Returns 0 if no suitable break is found.
    """

    # Look in the last 30 % of the segment to avoid overly small chunks
    search_start = max(0, len(segment) * 70 // 100)
    search_area = segment[search_start:]

    # Priority 1: double newline (paragraph break)
    idx = search_area.rfind("\n\n")
    if idx != -1:
        return search_start + idx + 2  # include the break

    # Priority 2: sentence end (". ")
    idx = search_area.rfind(". ")
    if idx != -1:
        return search_start + idx + 2

    # Priority 3: single newline
    idx = search_area.rfind("\n")
    if idx != -1:
        return search_start + idx + 1

    # Priority 4: space (word boundary)
    idx = search_area.rfind(" ")
    if idx != -1:
        return search_start + idx + 1

    return 0  # no clean break found


# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------

def process_document(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 100,
) -> list[str]:
    """
    Process a full document's text through the pipeline.

    Currently performs:
    1. Text chunking.

    Future extensions (async):
    2. Per-chunk AI analysis.
    3. Chunk-level scoring.
    4. Aggregated report generation.

    Parameters
    ----------
    text : str
        The full extracted document text.
    chunk_size : int
        Maximum characters per chunk.
    overlap : int
        Overlap between consecutive chunks.

    Returns
    -------
    list[str]
        Ordered list of processed text chunks.
    """

    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    logger.info(
        "Processed document: %d chars → %d chunks",
        len(text), len(chunks),
    )

    return chunks
