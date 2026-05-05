"""
Delfhos benchmark runner.

Uses native Delfhos APIs:
- @tool decorator (string-returning — safer with Delfhos's code-gen architecture)
- Agent with confirm=False for unattended benchmark runs
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from delfhos import Agent, tool

from .config import MODEL, NUM_RUNS
from .tasks import (
    TASK1_PROMPT, TASK2_PROMPT, TASK3_PROMPT, TASK4_PROMPT,
    _categorize_logic, _calc_roi_logic,
    _analyze_headcount_logic,
    _sort_tickets_logic,
)
from .results import RunResult

LIBRARY = "Delfhos"

# ── Tool definitions ──────────────────────────────────────────

@tool(confirm=False)
def categorize_expenses(items: list) -> str:
    """Categorize a list of expense items by type and compute totals.
    Each item must be a dict with 'description' (str) and 'amount' (float).
    Returns a formatted text report with totals per category."""
    r = _categorize_logic(items)
    lines = ["Expense Category Report:"]
    for k, v in r["totals"].items():
        lines.append(f"  {k}: ${v:.2f}")
    return "\n".join(lines)


@tool(confirm=False)
def calculate_quarterly_roi(quarters: list) -> str:
    """Calculate ROI (Revenue / Marketing) for each quarter.
    Each element must be a dict with 'quarter' (str), 'revenue' (float), 'marketing' (float).
    Returns a formatted table of ROI values."""
    data = _calc_roi_logic(quarters)
    lines = ["Quarterly ROI:"]
    for q in data:
        lines.append(f"  {q['quarter']}: {q['roi']}x (Revenue ${q['revenue']:,} / Marketing ${q['marketing']:,})")
    return "\n".join(lines)


@tool(confirm=False)
def generate_executive_summary(best_quarter: str, worst_quarter: str,
                               best_roi: float, worst_roi: float, avg_roi: float) -> str:
    """Generate a board-ready executive summary paragraph.
    Pass the best/worst quarter names, their ROI values, and the overall average ROI."""
    return (
        f"Executive Summary: The company achieved an average marketing ROI of {avg_roi:.2f}x. "
        f"{best_quarter} delivered the strongest return ({best_roi:.2f}x), "
        f"while {worst_quarter} was the weakest ({worst_roi:.2f}x). "
        f"The overall trend shows solid and improving marketing efficiency."
    )


@tool(confirm=False)
def analyze_headcount(departments: dict) -> str:
    """Analyse headcount per department.
    departments: dict mapping department name to list of [name, level] pairs.
    Returns a formatted breakdown table."""
    stats = _analyze_headcount_logic(departments)
    lines = ["Department Headcount:"]
    for dept, s in sorted(stats.items(), key=lambda x: -x[1]["total"]):
        lines.append(f"  {dept}: {s['total']} total ({s['senior']} senior, {s['junior']} junior)")
    return "\n".join(lines)


@tool(confirm=False)
def generate_workforce_report(largest_dept: str, smallest_dept: str,
                              total_employees: int, senior_count: int, junior_count: int) -> str:
    """Generate a formatted HR workforce distribution report.
    Pass the largest/smallest department names, total employee count, and senior/junior counts."""
    senior_pct = round(senior_count / total_employees * 100) if total_employees else 0
    junior_pct = 100 - senior_pct
    return (
        f"=== Workforce Distribution Report ===\n"
        f"Total Employees: {total_employees}\n"
        f"Senior / Junior: {senior_count} / {junior_count} ({senior_pct}% / {junior_pct}%)\n"
        f"Largest Department: {largest_dept}\n"
        f"Smallest Department: {smallest_dept}"
    )


@tool(confirm=False)
def parse_and_sort_tickets(tickets: list) -> str:
    """Parse and sort IT tickets by severity (critical → high → low).
    Each ticket must be a dict with 'id' (str), 'description' (str), 'severity' (str).
    Returns a sorted, formatted list."""
    sorted_t = _sort_tickets_logic(tickets)
    lines = ["Sorted Tickets (critical → high → low):"]
    for t in sorted_t:
        lines.append(f"  [{t['severity'].upper():8s}] {t['id']}: {t['description']}")
    return "\n".join(lines)


@tool(confirm=False)
def generate_action_plan(tickets_summary: str) -> str:
    """Generate a prioritised IT action plan from a sorted tickets summary string.
    Pass the output of parse_and_sort_tickets directly.
    Returns a structured action plan with response-time targets."""
    response_times = {"CRITICAL": "Immediate (< 15 min)", "HIGH": "Within 2 hours", "LOW": "Within 24 hours"}
    lines = ["=== IT Action Plan ==="]
    for line in tickets_summary.splitlines():
        if line.strip().startswith("["):
            for sev, rt in response_times.items():
                if f"[{sev}" in line:
                    lines.append(line + f"  → Response: {rt}")
                    break
            else:
                lines.append(line)
        else:
            lines.append(line)
    return "\n".join(lines)


# ── Task runners ──────────────────────────────────────────────

def _run(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    try:
        agent = Agent(tools=tools, llm=MODEL, verbose=False, retry_count=3)
        t0 = time.perf_counter()
        result = agent.run(prompt)
        duration_ms = int((time.perf_counter() - t0) * 1000)

        input_tokens = output_tokens = None
        try:
            task_count = agent.usage.task
            input_tokens = task_count.input
            output_tokens = task_count.output
        except Exception:
            pass

        agent.stop()

        return RunResult(
            task_id=task_id, task_name=task_name, library=LIBRARY, run_number=run_number,
            success=result.status, duration_ms=duration_ms,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=result.cost_usd, output_text=result.text[:300], error=result.error,
        )
    except Exception as e:
        return RunResult(
            task_id=task_id, task_name=task_name, library=LIBRARY, run_number=run_number,
            success=False, duration_ms=0, input_tokens=None, output_tokens=None,
            cost_usd=None, output_text="", error=str(e),
        )


def run_all() -> list[RunResult]:
    results = []

    tasks = [
        (1, "Expense Categorisation",  TASK1_PROMPT, [categorize_expenses]),
        (2, "Quarterly ROI Analysis",  TASK2_PROMPT, [calculate_quarterly_roi, generate_executive_summary]),
        (3, "HR Headcount Report",     TASK3_PROMPT, [analyze_headcount, generate_workforce_report]),
        (4, "IT Ticket Prioritisation", TASK4_PROMPT, [parse_and_sort_tickets, generate_action_plan]),
    ]

    for task_id, task_name, prompt, tools in tasks:
        for run_num in range(1, NUM_RUNS + 1):
            results.append(_run(task_id, task_name, prompt, tools, run_num))

    return results
