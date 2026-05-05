"""
AutoGen benchmark runner.

Uses AutoGen 0.4+ (autogen-agentchat):
- AssistantAgent with tool calling
- OpenAIChatCompletionClient pointed at Gemini's OpenAI-compatible endpoint
- asyncio.run() wrapper for synchronous benchmark interface
- Token counts from agent.actual_usage_summary (prompt_tokens / completion_tokens)
"""

import asyncio
import time
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .config import MODEL, GOOGLE_API_KEY, NUM_RUNS
from .tasks import (
    TASK1_PROMPT, TASK2_PROMPT, TASK3_PROMPT, TASK4_PROMPT,
    _categorize_logic, _calc_roi_logic, _exec_summary_logic,
    _analyze_headcount_logic, _workforce_report_logic,
    _sort_tickets_logic, _action_plan_logic,
)
from .results import RunResult, estimate_cost

LIBRARY = "AutoGen"

# Gemini OpenAI-compatible endpoint
_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _j(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


# ─── Tool definitions (plain callables — AutoGen wraps automatically) ──────

def categorize_expenses(expenses_json: str) -> str:
    """Categorize a list of expense items by type and compute totals.
    Input: JSON array of objects with 'description' (str) and 'amount' (float)."""
    return json.dumps(_categorize_logic(_j(expenses_json)))


def calculate_quarterly_roi(quarters_json: str) -> str:
    """Calculate ROI (revenue / marketing spend) for each quarter.
    Input: JSON array with 'quarter', 'revenue', 'marketing' fields."""
    return json.dumps(_calc_roi_logic(_j(quarters_json)))


def generate_executive_summary(roi_data_json: str) -> str:
    """Generate a board-ready executive summary paragraph from quarterly ROI data.
    Input: JSON array returned by calculate_quarterly_roi (must have 'roi' field per item)."""
    data = _j(roi_data_json)
    if not isinstance(data, list):
        data = _j(str(data))
    return _exec_summary_logic(data)


def analyze_headcount(departments_json: str) -> str:
    """Analyse headcount per department.
    Input: JSON object mapping department name to list of [name, level] pairs."""
    return json.dumps(_analyze_headcount_logic(_j(departments_json)))


def generate_workforce_report(stats_json: str) -> str:
    """Generate a formatted HR workforce distribution report.
    Input: JSON object returned by analyze_headcount."""
    return _workforce_report_logic(_j(stats_json))


def parse_and_sort_tickets(tickets_json: str) -> str:
    """Parse and sort IT support tickets by severity (critical → high → low).
    Input: JSON array with 'id', 'description', 'severity' fields."""
    return json.dumps(_sort_tickets_logic(_j(tickets_json)))


def generate_action_plan(sorted_tickets_json: str) -> str:
    """Generate a prioritised IT action plan from sorted tickets.
    Input: JSON array returned by parse_and_sort_tickets."""
    return _action_plan_logic(_j(sorted_tickets_json))


# ─── Runner ───────────────────────────────────────────────────

def _make_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=MODEL,
        base_url=_GEMINI_BASE_URL,
        api_key=GOOGLE_API_KEY,
        model_capabilities={
            "vision": False,
            "function_calling": True,
            "json_output": True,
        },
    )


async def _run_async(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    model_client = _make_client()
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=tools,
        system_message=(
            "You are a helpful business assistant. "
            "Use the available tools to complete the task accurately."
        ),
    )

    t0 = time.perf_counter()
    result = await agent.run(task=prompt)
    duration_ms = int((time.perf_counter() - t0) * 1000)

    # Extract final text answer (last non-empty TextMessage from assistant)
    answer = ""
    for msg in reversed(result.messages):
        content = getattr(msg, "content", None)
        if isinstance(content, str) and content.strip():
            answer = content
            break

    # Token counts — sum per-message models_usage (most reliable in 0.4+)
    input_tokens = output_tokens = None
    try:
        for msg in result.messages:
            mu = getattr(msg, "models_usage", None)
            if mu:
                input_tokens = (input_tokens or 0) + getattr(mu, "prompt_tokens", 0)
                output_tokens = (output_tokens or 0) + getattr(mu, "completion_tokens", 0)
    except Exception:
        pass

    # Fallback: try model_client.actual_usage()
    if input_tokens is None:
        try:
            usage = model_client.actual_usage()
            if usage:
                input_tokens = getattr(usage, "prompt_tokens", None)
                output_tokens = getattr(usage, "completion_tokens", None)
        except Exception:
            pass

    cost = (
        estimate_cost(int(input_tokens), int(output_tokens))
        if input_tokens is not None and output_tokens is not None
        else None
    )

    await model_client.close()

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


def _run(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    try:
        return asyncio.run(_run_async(task_id, task_name, prompt, tools, run_number))
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
