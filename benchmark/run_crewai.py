"""
CrewAI benchmark runner.

Uses CrewAI with LiteLLM for Gemini:
- Single Agent + single Task per run (no multi-agent overhead)
- Tools defined with @tool decorator from crewai.tools
- Token counts from crew_output.token_usage (prompt_tokens / completion_tokens)
"""

import time
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool as crewai_tool

from .config import CREWAI_MODEL, NUM_RUNS
from .tasks import (
    TASK1_PROMPT, TASK2_PROMPT, TASK3_PROMPT, TASK4_PROMPT,
    _categorize_logic, _calc_roi_logic, _exec_summary_logic,
    _analyze_headcount_logic, _workforce_report_logic,
    _sort_tickets_logic, _action_plan_logic,
)
from .results import RunResult, estimate_cost

LIBRARY = "CrewAI"


def _j(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


# ─── Tool definitions ──────────────────────────────────────────

@crewai_tool
def categorize_expenses(expenses_json: str) -> str:
    """Categorize a list of expense items by type and compute totals.
    Input: JSON array of objects with 'description' (str) and 'amount' (float)."""
    return json.dumps(_categorize_logic(_j(expenses_json)))


@crewai_tool
def calculate_quarterly_roi(quarters_json: str) -> str:
    """Calculate ROI (revenue / marketing spend) for each quarter.
    Input: JSON array with 'quarter', 'revenue', 'marketing' fields."""
    return json.dumps(_calc_roi_logic(_j(quarters_json)))


@crewai_tool
def generate_executive_summary(roi_data_json: str) -> str:
    """Generate a board-ready executive summary paragraph from quarterly ROI data.
    Input: JSON array returned by calculate_quarterly_roi (must have 'roi' field per item)."""
    data = _j(roi_data_json)
    if not isinstance(data, list):
        data = _j(str(data))
    return _exec_summary_logic(data)


@crewai_tool
def analyze_headcount(departments_json: str) -> str:
    """Analyse headcount per department.
    Input: JSON object mapping department name to list of [name, level] pairs."""
    return json.dumps(_analyze_headcount_logic(_j(departments_json)))


@crewai_tool
def generate_workforce_report(stats_json: str) -> str:
    """Generate a formatted HR workforce distribution report.
    Input: JSON object returned by analyze_headcount."""
    return _workforce_report_logic(_j(stats_json))


@crewai_tool
def parse_and_sort_tickets(tickets_json: str) -> str:
    """Parse and sort IT support tickets by severity (critical → high → low).
    Input: JSON array with 'id', 'description', 'severity' fields."""
    return json.dumps(_sort_tickets_logic(_j(tickets_json)))


@crewai_tool
def generate_action_plan(sorted_tickets_json: str) -> str:
    """Generate a prioritised IT action plan from sorted tickets.
    Input: JSON array returned by parse_and_sort_tickets."""
    return _action_plan_logic(_j(sorted_tickets_json))


# ─── Runner ───────────────────────────────────────────────────

def _run(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    try:
        agent = Agent(
            role="Business Assistant",
            goal="Complete the assigned business task accurately using the available tools.",
            backstory="You are an experienced business analyst with expertise in finance, HR, and IT operations.",
            tools=tools,
            llm=CREWAI_MODEL,
            verbose=False,
            allow_delegation=False,
        )
        task = Task(
            description=prompt,
            expected_output="A complete and accurate analysis based on the tools provided.",
            agent=agent,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )

        t0 = time.perf_counter()
        crew_output = crew.kickoff()
        duration_ms = int((time.perf_counter() - t0) * 1000)

        answer = str(crew_output) if crew_output else ""

        # Token counts from CrewOutput.token_usage (UsageMetrics)
        input_tokens = output_tokens = cost = None
        try:
            tu = getattr(crew_output, "token_usage", None)
            if tu is None:
                tu = getattr(crew, "usage_metrics", None)
            if tu is not None:
                if hasattr(tu, "model_dump"):
                    d = tu.model_dump()
                elif hasattr(tu, "dict"):
                    d = tu.dict()
                elif isinstance(tu, dict):
                    d = tu
                else:
                    d = {k: getattr(tu, k, None) for k in (
                        "prompt_tokens", "completion_tokens",
                        "total_prompt_tokens", "total_completion_tokens",
                    )}
                input_tokens = d.get("prompt_tokens") or d.get("total_prompt_tokens")
                output_tokens = d.get("completion_tokens") or d.get("total_completion_tokens")
            if input_tokens is not None and output_tokens is not None:
                cost = estimate_cost(int(input_tokens), int(output_tokens))
        except Exception:
            pass

        return RunResult(
            task_id=task_id,
            task_name=task_name,
            library=LIBRARY,
            run_number=run_number,
            success=bool(answer),
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            output_text=answer[:300],
        )
    except Exception as e:
        return RunResult(
            task_id=task_id,
            task_name=task_name,
            library=LIBRARY,
            run_number=run_number,
            success=False,
            duration_ms=0,
            input_tokens=None,
            output_tokens=None,
            cost_usd=None,
            output_text="",
            error=str(e),
        )


def run_all() -> list[RunResult]:
    results = []

    tasks = [
        (1, "Expense Categorisation",   TASK1_PROMPT, [categorize_expenses]),
        (2, "Quarterly ROI Analysis",   TASK2_PROMPT, [calculate_quarterly_roi, generate_executive_summary]),
        (3, "HR Headcount Report",      TASK3_PROMPT, [analyze_headcount, generate_workforce_report]),
        (4, "IT Ticket Prioritisation", TASK4_PROMPT, [parse_and_sort_tickets, generate_action_plan]),
    ]

    for task_id, task_name, prompt, tools in tasks:
        for run_num in range(1, NUM_RUNS + 1):
            results.append(_run(task_id, task_name, prompt, tools, run_num))

    return results
