"""
SmolAgents benchmark runner.

Uses HuggingFace smolagents:
- ToolCallingAgent with LiteLLMModel (Gemini via LiteLLM)
- Tools defined with @tool decorator (requires type hints + Google-style docstring)
- Token counts from agent.monitor (total_input_token_count / total_output_token_count)
"""

import time
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from smolagents import ToolCallingAgent, LiteLLMModel, tool as smolagents_tool

from .config import MODEL, GOOGLE_API_KEY, NUM_RUNS
from .tasks import (
    TASK1_PROMPT, TASK2_PROMPT, TASK3_PROMPT, TASK4_PROMPT,
    _categorize_logic, _calc_roi_logic, _exec_summary_logic,
    _analyze_headcount_logic, _workforce_report_logic,
    _sort_tickets_logic, _action_plan_logic,
)
from .results import RunResult, estimate_cost

LIBRARY = "SmolAgents"

# LiteLLM model string for Gemini
_LITELLM_MODEL = f"gemini/{MODEL}"


def _j(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


# ─── Tool definitions ──────────────────────────────────────────
# smolagents @tool requires: type annotations, docstring with Args section

@smolagents_tool
def categorize_expenses(expenses_json: str) -> str:
    """Categorize a list of expense items by type and compute totals.

    Args:
        expenses_json: JSON array of objects with 'description' (str) and 'amount' (float).

    Returns:
        JSON object with categorized items and totals per category.
    """
    return json.dumps(_categorize_logic(_j(expenses_json)))


@smolagents_tool
def calculate_quarterly_roi(quarters_json: str) -> str:
    """Calculate ROI (revenue / marketing spend) for each quarter.

    Args:
        quarters_json: JSON array with 'quarter', 'revenue', 'marketing' fields.

    Returns:
        JSON array with ROI values added to each quarter object.
    """
    return json.dumps(_calc_roi_logic(_j(quarters_json)))


@smolagents_tool
def generate_executive_summary(roi_data_json: str) -> str:
    """Generate a board-ready executive summary paragraph from quarterly ROI data.

    Args:
        roi_data_json: JSON array returned by calculate_quarterly_roi (must have 'roi' field per item).

    Returns:
        A formatted executive summary string.
    """
    data = _j(roi_data_json)
    if not isinstance(data, list):
        data = _j(str(data))
    return _exec_summary_logic(data)


@smolagents_tool
def analyze_headcount(departments_json: str) -> str:
    """Analyse headcount per department and return per-department stats.

    Args:
        departments_json: JSON object mapping department name to list of [name, level] pairs.

    Returns:
        JSON object with total, senior, and junior counts per department.
    """
    return json.dumps(_analyze_headcount_logic(_j(departments_json)))


@smolagents_tool
def generate_workforce_report(stats_json: str) -> str:
    """Generate a formatted HR workforce distribution report.

    Args:
        stats_json: JSON object returned by analyze_headcount.

    Returns:
        A formatted workforce report string.
    """
    return _workforce_report_logic(_j(stats_json))


@smolagents_tool
def parse_and_sort_tickets(tickets_json: str) -> str:
    """Parse and sort IT support tickets by severity (critical → high → low).

    Args:
        tickets_json: JSON array with 'id', 'description', 'severity' fields.

    Returns:
        JSON array of tickets sorted by severity.
    """
    return json.dumps(_sort_tickets_logic(_j(tickets_json)))


@smolagents_tool
def generate_action_plan(sorted_tickets_json: str) -> str:
    """Generate a prioritised IT action plan with response-time targets.

    Args:
        sorted_tickets_json: JSON array returned by parse_and_sort_tickets.

    Returns:
        A formatted action plan string with response times.
    """
    return _action_plan_logic(_j(sorted_tickets_json))


# ─── Runner ───────────────────────────────────────────────────

def _make_model() -> LiteLLMModel:
    return LiteLLMModel(
        model_id=_LITELLM_MODEL,
        api_key=GOOGLE_API_KEY,
    )


def _run(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    try:
        model = _make_model()
        agent = ToolCallingAgent(
            tools=tools,
            model=model,
            max_steps=10,
        )

        t0 = time.perf_counter()
        answer = agent.run(prompt)
        duration_ms = int((time.perf_counter() - t0) * 1000)

        answer_str = str(answer) if answer is not None else ""

        # Token counts from agent.monitor
        input_tokens = output_tokens = cost = None
        try:
            monitor = getattr(agent, "monitor", None)
            if monitor is not None:
                # Try get_total_token_counts() method first
                if hasattr(monitor, "get_total_token_counts"):
                    counts = monitor.get_total_token_counts()
                    if isinstance(counts, dict):
                        input_tokens = counts.get("input") or counts.get("input_tokens")
                        output_tokens = counts.get("output") or counts.get("output_tokens")
                    else:
                        input_tokens = getattr(counts, "input_tokens", None) or getattr(counts, "input", None)
                        output_tokens = getattr(counts, "output_tokens", None) or getattr(counts, "output", None)
                # Fall back to direct attributes
                if input_tokens is None:
                    input_tokens = getattr(monitor, "total_input_token_count", None)
                    output_tokens = getattr(monitor, "total_output_token_count", None)
            # Final fallback: sum per-step usage from agent.memory
            if input_tokens is None:
                memory = getattr(agent, "memory", None)
                steps = getattr(memory, "steps", None) if memory else None
                if steps:
                    in_sum = out_sum = 0
                    found = False
                    for step in steps:
                        usage = getattr(step, "token_usage", None) or getattr(step, "input_token_count", None)
                        if usage is not None:
                            found = True
                            if hasattr(usage, "input_tokens"):
                                in_sum += getattr(usage, "input_tokens", 0) or 0
                                out_sum += getattr(usage, "output_tokens", 0) or 0
                            else:
                                in_sum += getattr(step, "input_token_count", 0) or 0
                                out_sum += getattr(step, "output_token_count", 0) or 0
                    if found:
                        input_tokens, output_tokens = in_sum, out_sum
            if input_tokens is not None and output_tokens is not None:
                cost = estimate_cost(int(input_tokens), int(output_tokens))
        except Exception:
            pass

        return RunResult(
            task_id=task_id,
            task_name=task_name,
            library=LIBRARY,
            run_number=run_number,
            success=bool(answer_str),
            duration_ms=duration_ms,
            input_tokens=int(input_tokens) if input_tokens is not None else None,
            output_tokens=int(output_tokens) if output_tokens is not None else None,
            cost_usd=cost,
            output_text=answer_str[:300],
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
