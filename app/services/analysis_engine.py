"""
Inefficiency and cost analysis engine.

Takes structured workflow data (from the workflow analyzer), sends it
to the LLM for inefficiency identification, then calculates financial
impact based on the provided hourly rate.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from app.services.llm_service import LLMError, LLMService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HOURLY_RATE = 15.0      # £15 / hour
WORKING_DAYS_PER_MONTH = 22


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_analysis_prompt(workflow_data: dict[str, Any]) -> str:
    """
    Build the inefficiency-analysis prompt from structured workflow data.
    """

    data_json = json.dumps(workflow_data, indent=2, default=str)

    return (
        "You are a business operations consultant.\n\n"
        "Using the workflow data:\n\n"
        "1. Identify inefficiencies\n"
        "2. Estimate time lost per day (hours)\n"
        "3. Identify revenue leakage points\n\n"
        "{\n"
        '  "inefficiencies": [\n'
        '    {"issue": "", "recommendation": ""}\n'
        '  ],\n'
        '  "time_loss_hours_per_day": number,\n'
        '  "revenue_leakage": [],\n'
        '  "implementation_plan": {\n'
        '    "phase_1": [],\n'
        '    "phase_2": []\n'
        '  }\n'
        "}\n\n"
        "Rules:\n"
        "- Each inefficiency must map to a specific, actionable recommendation.\n"
        "- time_loss_hours_per_day should be a realistic decimal number.\n"
        "- Each revenue leakage point should be a string.\n"
        "- Phase 1 (quick wins) and Phase 2 (systemic improvements) should be actionable strings.\n"
        "- Base your analysis only on the provided data.\n\n"
        f"Workflow data:\n{data_json}"
    )


# ---------------------------------------------------------------------------
# JSON response parsing
# ---------------------------------------------------------------------------

def _extract_json(raw: str) -> dict[str, Any]:
    """
    Parse the LLM response into a dict.

    Handles markdown code fences and surrounding text.
    """

    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse analysis response as JSON: %.200s…", text)
    return {
        "inefficiencies": [],
        "time_loss_hours_per_day": 0.0,
        "revenue_leakage": [],
        "implementation_plan": {"phase_1": [], "phase_2": []},
    }


def _validate_analysis(data: dict[str, Any]) -> dict[str, Any]:
    """Ensure the parsed result has the expected shape and types."""

    inefficiencies = data.get("inefficiencies", [])
    if not isinstance(inefficiencies, list):
        inefficiencies = []
        
    validated_inefficiencies = []
    for i in inefficiencies:
        if isinstance(i, dict) and "issue" in i and "recommendation" in i:
            validated_inefficiencies.append({
                "issue": str(i["issue"]),
                "recommendation": str(i["recommendation"])
            })

    time_loss = data.get("time_loss_hours_per_day", 0.0)
    try:
        time_loss = float(time_loss)
    except (TypeError, ValueError):
        time_loss = 0.0
    # Sanity-cap at 24 hours
    time_loss = max(0.0, min(time_loss, 24.0))

    revenue_leakage = data.get("revenue_leakage", [])
    if not isinstance(revenue_leakage, list):
        revenue_leakage = []
        
    impl_plan = data.get("implementation_plan", {})
    if not isinstance(impl_plan, dict):
        impl_plan = {}
        
    phase_1 = impl_plan.get("phase_1", [])
    phase_2 = impl_plan.get("phase_2", [])

    return {
        "inefficiencies": validated_inefficiencies,
        "time_loss_hours_per_day": round(time_loss, 2),
        "revenue_leakage": [str(r) for r in revenue_leakage if r],
        "implementation_plan": {
            "phase_1": [str(x) for x in phase_1 if x] if isinstance(phase_1, list) else [],
            "phase_2": [str(x) for x in phase_2 if x] if isinstance(phase_2, list) else [],
        }
    }


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------

def calculate_cost(
    time_loss_hours_per_day: float,
    hourly_rate: float = DEFAULT_HOURLY_RATE,
    working_days: int = WORKING_DAYS_PER_MONTH,
) -> dict[str, float]:
    """
    Calculate the financial impact of time losses.

    Returns
    -------
    dict with keys:
        - daily_cost
        - monthly_cost
        - annual_cost
    """

    daily = round(time_loss_hours_per_day * hourly_rate, 2)
    monthly = round(daily * working_days, 2)
    annual = round(monthly * 12, 2)

    return {
        "daily_cost": daily,
        "monthly_cost": monthly,
        "annual_cost": annual,
        "cost_explanation": f"Calculation based on {time_loss_hours_per_day} hours lost per day × £{hourly_rate}/hr × {working_days} days/month."
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_inefficiencies(
    workflow_data: dict[str, Any],
    hourly_rate: Optional[float] = None,
    llm: Optional[LLMService] = None,
) -> dict[str, Any]:
    """
    Analyse structured workflow data for inefficiencies and calculate
    the financial impact.

    Parameters
    ----------
    workflow_data : dict
        Structured output from ``workflow_analyzer.analyze_workflow()``.
        Expected keys: ``workflow_steps``, ``manual_tasks``,
        ``repeated_tasks``, ``bottlenecks``, ``delays``.
    hourly_rate : float, optional
        Billable rate per hour. Defaults to £15.
    llm : LLMService, optional
        An existing LLM service instance.  If ``None``, a new one is created.

    Returns
    -------
    dict with keys:
        - inefficiencies: list[str]
        - time_loss_hours_per_day: float
        - revenue_leakage: list[str]
        - cost_analysis: {daily_cost, monthly_cost, annual_cost}
        - hourly_rate: float
    """

    rate = hourly_rate if hourly_rate is not None else DEFAULT_HOURLY_RATE

    if llm is None:
        llm = LLMService()

    prompt = _build_analysis_prompt(workflow_data)

    logger.info(
        "Running inefficiency analysis (hourly_rate=%.2f, prompt=%d chars)",
        rate, len(prompt),
    )

    try:
        raw_response = await llm.generate(prompt)
        parsed = _extract_json(raw_response)
        validated = _validate_analysis(parsed)

    except LLMError as exc:
        logger.error("LLM error during inefficiency analysis: %s", exc.detail)
        validated = {
            "inefficiencies": [],
            "time_loss_hours_per_day": 0.0,
            "revenue_leakage": [],
            "implementation_plan": {"phase_1": [], "phase_2": []},
        }

    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during inefficiency analysis: %s", exc)
        validated = {
            "inefficiencies": [],
            "time_loss_hours_per_day": 0.0,
            "revenue_leakage": [],
            "implementation_plan": {"phase_1": [], "phase_2": []},
        }

    # Calculate costs
    cost = calculate_cost(
        time_loss_hours_per_day=validated["time_loss_hours_per_day"],
        hourly_rate=rate,
    )

    result = {
        **validated,
        "cost_analysis": cost,
        "hourly_rate": rate,
    }

    logger.info(
        "Inefficiency analysis complete: %d inefficiencies, "
        "%.2f hrs/day lost, monthly cost=%.2f",
        len(result["inefficiencies"]),
        result["time_loss_hours_per_day"],
        cost["monthly_cost"],
    )

    return result
