"""
Workflow analysis service.

Sends each text chunk to the LLM with a structured extraction prompt,
parses the JSON responses, and aggregates findings across all chunks
into a single unified result.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from app.services.llm_service import LLMError, LLMService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

# Shape of a single chunk's analysis result
EMPTY_CHUNK_RESULT: dict[str, Any] = {
    "workflow_steps": [],
    "manual_tasks": [],
    "repeated_tasks": [],
    "bottlenecks": [],
    "delays": [],
}

# Keys that hold list values and should be merged across chunks
_LIST_KEYS = list(EMPTY_CHUNK_RESULT.keys())


# ---------------------------------------------------------------------------
# Prompt builder (kept out of llm_service per design contract)
# ---------------------------------------------------------------------------

def _build_extraction_prompt(chunk: str) -> str:
    """Build the structured extraction prompt for a single chunk."""

    return (
        "You are an operations analyst.\n\n"
        "Extract ONLY factual workflow information from the text.\n\n"
        "Return JSON:\n"
        "{\n"
        '  "workflow_steps": [{"step": "", "description": ""}],\n'
        '  "manual_tasks": [],\n'
        '  "repeated_tasks": [],\n'
        '  "bottlenecks": [],\n'
        '  "delays": []\n'
        "}\n\n"
        "Do not assume missing information.\n\n"
        f"Text:\n{chunk}"
    )


# ---------------------------------------------------------------------------
# JSON response parsing
# ---------------------------------------------------------------------------

def _extract_json(raw: str) -> dict[str, Any]:
    """
    Parse the LLM response into a dict.

    Handles common quirks:
    - Markdown code fences (```json ... ```)
    - Leading/trailing junk around the JSON block
    """

    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```\s*$", "", text)

    # Attempt direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find the first { ... } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse LLM response as JSON: %.200s…", text)
    return dict(EMPTY_CHUNK_RESULT)  # return empty structure


def _validate_chunk_result(data: dict[str, Any]) -> dict[str, Any]:
    """Ensure the parsed result has the expected keys and list types."""

    result: dict[str, Any] = {}
    for key in _LIST_KEYS:
        value = data.get(key, [])
        if not isinstance(value, list):
            value = []
        result[key] = value

    return result


# ---------------------------------------------------------------------------
# Per-chunk analysis
# ---------------------------------------------------------------------------

async def _analyze_chunk(
    llm: LLMService,
    chunk: str,
    chunk_index: int,
) -> dict[str, Any]:
    """
    Send a single *chunk* to the LLM and return the parsed result.

    On failure, logs the error and returns an empty structure so the
    rest of the pipeline isn't blocked.
    """

    prompt = _build_extraction_prompt(chunk)

    try:
        raw_response = await llm.generate(prompt)
        parsed = _extract_json(raw_response)
        result = _validate_chunk_result(parsed)

        logger.info(
            "Chunk %d: %d steps, %d manual, %d repeated, %d bottlenecks, %d delays",
            chunk_index,
            len(result["workflow_steps"]),
            len(result["manual_tasks"]),
            len(result["repeated_tasks"]),
            len(result["bottlenecks"]),
            len(result["delays"]),
        )
        return result

    except LLMError as exc:
        logger.error("Chunk %d LLM error: %s", chunk_index, exc.detail)
        return dict(EMPTY_CHUNK_RESULT)

    except Exception as exc:  # noqa: BLE001
        logger.error("Chunk %d unexpected error: %s", chunk_index, exc)
        return dict(EMPTY_CHUNK_RESULT)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _deduplicate_steps(
    steps: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Remove duplicate workflow steps based on step name."""

    seen: set[str] = set()
    unique: list[dict[str, str]] = []

    for step in steps:
        key = step.get("step", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(step)

    return unique


def _deduplicate_strings(items: list[str]) -> list[str]:
    """Remove duplicate strings (case-insensitive)."""

    seen: set[str] = set()
    unique: list[str] = []

    for item in items:
        normalised = item.strip().lower()
        if normalised and normalised not in seen:
            seen.add(normalised)
            unique.append(item.strip())

    return unique


def _aggregate_results(
    chunk_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Merge analysis results from multiple chunks into a single
    de-duplicated structure.
    """

    merged: dict[str, Any] = {key: [] for key in _LIST_KEYS}

    for result in chunk_results:
        for key in _LIST_KEYS:
            merged[key].extend(result.get(key, []))

    # De-duplicate
    merged["workflow_steps"] = _deduplicate_steps(merged["workflow_steps"])
    merged["manual_tasks"] = _deduplicate_strings(merged["manual_tasks"])
    merged["repeated_tasks"] = _deduplicate_strings(merged["repeated_tasks"])
    merged["bottlenecks"] = _deduplicate_strings(merged["bottlenecks"])
    merged["delays"] = _deduplicate_strings(merged["delays"])

    return merged


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_workflow(
    chunks: list[str],
    llm: Optional[LLMService] = None,
) -> dict[str, Any]:
    """
    Analyse a list of text *chunks* through the LLM and return
    aggregated, de-duplicated workflow findings.

    Parameters
    ----------
    chunks : list[str]
        Ordered text chunks from the document.
    llm : LLMService, optional
        An existing LLM service instance.  If ``None``, a new one
        is created using the default provider.

    Returns
    -------
    dict[str, Any]
        Merged analysis with keys:
        ``workflow_steps``, ``manual_tasks``, ``repeated_tasks``,
        ``bottlenecks``, ``delays``.
    """

    if not chunks:
        logger.warning("analyze_workflow called with no chunks")
        return dict(EMPTY_CHUNK_RESULT)

    if llm is None:
        llm = LLMService()

    logger.info("Starting workflow analysis: %d chunks", len(chunks))

    # Analyse each chunk sequentially
    # (switch to asyncio.gather for parallelism when rate limits allow)
    chunk_results: list[dict[str, Any]] = []
    for i, chunk in enumerate(chunks):
        result = await _analyze_chunk(llm, chunk, chunk_index=i)
        chunk_results.append(result)

    # Aggregate and de-duplicate
    aggregated = _aggregate_results(chunk_results)

    logger.info(
        "Workflow analysis complete: %d steps, %d manual, "
        "%d repeated, %d bottlenecks, %d delays",
        len(aggregated["workflow_steps"]),
        len(aggregated["manual_tasks"]),
        len(aggregated["repeated_tasks"]),
        len(aggregated["bottlenecks"]),
        len(aggregated["delays"]),
    )

    return aggregated
