"""
Report generation service.

Takes the structured workflow analysis and cost data and produces
a clean, readable Markdown audit report.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_report(
    workflow_data: dict[str, Any],
    cost_data: dict[str, Any],
    *,
    filename: Optional[str] = None,
    job_id: Optional[str] = None,
) -> str:
    """
    Generate a structured Markdown audit report.

    Parameters
    ----------
    workflow_data : dict
        Output from ``workflow_analyzer.analyze_workflow()``.
        Keys: ``workflow_steps``, ``manual_tasks``, ``repeated_tasks``,
        ``bottlenecks``, ``delays``.
    cost_data : dict
        Output from ``analysis_engine.analyze_inefficiencies()``.
        Keys: ``inefficiencies``, ``time_loss_hours_per_day``,
        ``revenue_leakage``, ``cost_analysis``, ``hourly_rate``.
    filename : str, optional
        Original uploaded filename for the header.
    job_id : str, optional
        Job identifier for traceability.

    Returns
    -------
    str
        Complete Markdown report.
    """

    sections = [
        _header(filename, job_id),
        _executive_summary(workflow_data, cost_data),
        _current_workflow(workflow_data),
        _key_inefficiencies(cost_data),
        _revenue_cost_leakage(cost_data),
        _implementation_plan(cost_data),
        _recommendations(workflow_data, cost_data),
        _next_steps(workflow_data, cost_data),
        _footer(),
    ]

    report = "\n\n".join(s for s in sections if s)

    logger.info("Generated report: %d characters", len(report))
    return report


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _header(filename: Optional[str], job_id: Optional[str]) -> str:
    """Report title and metadata."""

    lines = [
        "# 📋 Eenera Workflow Audit Report",
        "",
    ]

    meta_parts = []
    if filename:
        meta_parts.append(f"**Document:** {filename}")
    if job_id:
        meta_parts.append(f"**Job ID:** `{job_id}`")
    meta_parts.append(
        f"**Generated:** {datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}"
    )

    lines.append(" · ".join(meta_parts))
    lines.append("")
    lines.append("---")

    return "\n".join(lines)


def _executive_summary(
    workflow: dict[str, Any],
    cost: dict[str, Any],
) -> str:
    """High-level overview with the most important numbers."""

    steps = workflow.get("workflow_steps", [])
    manual = workflow.get("manual_tasks", [])
    bottlenecks = workflow.get("bottlenecks", [])
    delays = workflow.get("delays", [])

    time_loss = cost.get("time_loss_hours_per_day", 0.0)
    cost_info = cost.get("cost_analysis", {})
    monthly = cost_info.get("monthly_cost", 0.0)
    annual = cost_info.get("annual_cost", 0.0)
    hourly_rate = cost.get("hourly_rate", 15.0)
    inefficiencies = cost.get("inefficiencies", [])

    lines = [
        "## 📌 Executive Summary",
        "",
    ]

    # Key metrics table
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Workflow steps identified | **{len(steps)}** |")
    lines.append(f"| Manual tasks | **{len(manual)}** |")
    lines.append(f"| Bottlenecks | **{len(bottlenecks)}** |")
    lines.append(f"| Delays found | **{len(delays)}** |")
    lines.append(f"| Inefficiencies detected | **{len(inefficiencies)}** |")
    lines.append(f"| Estimated time lost per day | **{time_loss:.1f} hours** |")
    lines.append(f"| 💷 Estimated monthly cost | **£{monthly:,.2f}** |")
    lines.append(f"| 💷 Estimated annual cost | **£{annual:,.2f}** |")
    lines.append(f"| Hourly rate used | £{hourly_rate:.2f} |")

    return "\n".join(lines)


def _current_workflow(workflow: dict[str, Any]) -> str:
    """Current workflow steps and identified issues."""

    steps = workflow.get("workflow_steps", [])
    manual = workflow.get("manual_tasks", [])
    repeated = workflow.get("repeated_tasks", [])
    bottlenecks = workflow.get("bottlenecks", [])
    delays = workflow.get("delays", [])

    lines = [
        "## 🔄 Current Workflow",
        "",
    ]

    # Steps
    if steps:
        lines.append("### Workflow Steps")
        lines.append("")
        for i, step in enumerate(steps, 1):
            name = step.get("step", "Unnamed step")
            desc = step.get("description", "")
            if desc:
                lines.append(f"{i}. **{name}** — {desc}")
            else:
                lines.append(f"{i}. **{name}**")
        lines.append("")
    else:
        lines.append("*No explicit workflow steps were identified in the document.*")
        lines.append("")

    # Manual tasks
    if manual:
        lines.append("### 🖐️ Manual Tasks")
        lines.append("")
        for task in manual:
            lines.append(f"- {task}")
        lines.append("")

    # Repeated tasks
    if repeated:
        lines.append("### 🔁 Repeated Tasks")
        lines.append("")
        for task in repeated:
            lines.append(f"- {task}")
        lines.append("")

    # Bottlenecks
    if bottlenecks:
        lines.append("### ⚠️ Bottlenecks")
        lines.append("")
        for item in bottlenecks:
            lines.append(f"- {item}")
        lines.append("")

    # Delays
    if delays:
        lines.append("### ⏳ Delays")
        lines.append("")
        for item in delays:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def _key_inefficiencies(cost: dict[str, Any]) -> str:
    """Inefficiencies identified by the analysis engine."""

    inefficiencies = cost.get("inefficiencies", [])
    time_loss = cost.get("time_loss_hours_per_day", 0.0)

    lines = [
        "## 🚨 Key Inefficiencies & Actionable Solutions",
        "",
    ]

    if inefficiencies:
        for i, item in enumerate(inefficiencies, 1):
            if isinstance(item, dict):
                lines.append(f"### {i}. {item.get('issue', 'Unknown Issue')}")
                lines.append(f"**Recommendation:** {item.get('recommendation', '')}")
                lines.append("")
            else:
                lines.append(f"{i}. {item}")
        lines.append("")
        lines.append(
            f"> ⏱️ **Total estimated time lost: {time_loss:.1f} hours per day**"
        )
    else:
        lines.append(
            "*No specific inefficiencies were identified. "
            "Consider providing more detailed workflow documentation.*"
        )

    return "\n".join(lines)


def _revenue_cost_leakage(cost: dict[str, Any]) -> str:
    """Revenue leakage points and financial impact."""

    leakage = cost.get("revenue_leakage", [])
    cost_info = cost.get("cost_analysis", {})
    daily = cost_info.get("daily_cost", 0.0)
    monthly = cost_info.get("monthly_cost", 0.0)
    annual = cost_info.get("annual_cost", 0.0)
    cost_explanation = cost_info.get("cost_explanation", "")

    lines = [
        "## 💸 Revenue & Cost Leakage",
        "",
    ]

    # Financial impact
    lines.append("### Financial Impact")
    lines.append("")
    if cost_explanation:
        lines.append(f"*{cost_explanation}*")
        lines.append("")
    lines.append("| Period | Estimated Cost |")
    lines.append("|--------|----------------|")
    lines.append(f"| Daily | £{daily:,.2f} |")
    lines.append(f"| **Monthly** | **£{monthly:,.2f}** |")
    lines.append(f"| Annual | £{annual:,.2f} |")
    lines.append("")

    # Leakage points
    if leakage:
        lines.append("### Revenue Leakage Points")
        lines.append("")
        for i, item in enumerate(leakage, 1):
            lines.append(f"{i}. {item}")
    else:
        lines.append(
            "*No specific revenue leakage points were identified.*"
        )

    return "\n".join(lines)


def _recommendations(
    workflow: dict[str, Any],
    cost: dict[str, Any],
) -> str:
    """Auto-generated recommendations based on the findings."""

    manual = workflow.get("manual_tasks", [])
    repeated = workflow.get("repeated_tasks", [])
    bottlenecks = workflow.get("bottlenecks", [])
    delays = workflow.get("delays", [])
    cost_info = cost.get("cost_analysis", {})
    monthly = cost_info.get("monthly_cost", 0.0)

    lines = [
        "## ✅ Eenera Recommendations",
        "",
    ]

    recs: list[str] = []

    if manual:
        recs.append(
            f"**Automate manual tasks** — {len(manual)} manual "
            f"task(s) identified that could be automated to reduce "
            f"human error and processing time."
        )

    if repeated:
        recs.append(
            f"**Eliminate duplication** — {len(repeated)} repeated "
            f"task(s) found. Consolidate these into single execution "
            f"points to save time."
        )

    if bottlenecks:
        recs.append(
            f"**Address bottlenecks** — {len(bottlenecks)} "
            f"bottleneck(s) are slowing down operations. Consider "
            f"parallel processing or delegation strategies."
        )

    if delays:
        recs.append(
            f"**Reduce delays** — {len(delays)} delay(s) "
            f"identified. Implement SLAs or automated reminders "
            f"to keep workflows moving."
        )

    if monthly > 0:
        recs.append(
            f"**Cost recovery potential** — Addressing the above "
            f"issues could recover up to **£{monthly:,.2f}/month** "
            f"in operational costs."
        )

    if not recs:
        recs.append(
            "The current workflow appears efficient based on the "
            "provided documentation. Consider a more detailed "
            "process mapping for deeper insights."
        )

    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {rec}")

    return "\n".join(lines)


def _next_steps(
    workflow: dict[str, Any],
    cost: dict[str, Any],
) -> str:
    """Concrete next steps for the organisation."""

    manual = workflow.get("manual_tasks", [])
    bottlenecks = workflow.get("bottlenecks", [])
    cost_info = cost.get("cost_analysis", {})
    monthly = cost_info.get("monthly_cost", 0.0)

    lines = [
        "## 🎯 Immediate Next Steps",
        "",
    ]

    steps: list[str] = [
        "Review this audit report with your operations team.",
    ]

    if manual:
        steps.append(
            "Prioritise the top manual tasks for automation evaluation."
        )

    if bottlenecks:
        steps.append(
            "Map out bottleneck dependencies and assign owners "
            "for resolution."
        )

    if monthly > 100:
        steps.append(
            "Schedule a process improvement workshop to address "
            "the top cost drivers."
        )

    steps.append(
        "Contact Eenera for a detailed automation roadmap and "
        "implementation support."
    )

    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}")

    return "\n".join(lines)


def _implementation_plan(cost: dict[str, Any]) -> str:
    """Recommended phased implementation plan."""
    
    impl_plan = cost.get("implementation_plan", {})
    phase_1 = impl_plan.get("phase_1", [])
    phase_2 = impl_plan.get("phase_2", [])
    
    if not phase_1 and not phase_2:
        return ""
        
    lines = [
        "## 🛠️ Recommended Implementation Plan",
        "",
    ]
    
    if phase_1:
        lines.append("### Phase 1: Quick Wins")
        lines.append("")
        for item in phase_1:
            lines.append(f"- {item}")
        lines.append("")
        
    if phase_2:
        lines.append("### Phase 2: System Improvements")
        lines.append("")
        for item in phase_2:
            lines.append(f"- {item}")
        lines.append("")
        
    return "\n".join(lines)


def _footer() -> str:
    """Report footer."""

    return (
        "---\n\n"
        "*This report was generated by **Eenera AI Workflow Audit System**. "
        "For questions or to discuss implementation of these recommendations, "
        "contact the Eenera team.*"
    )
