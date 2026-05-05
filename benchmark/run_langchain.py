"""
LangChain benchmark runner.

Uses LangChain 0.3+ with LangGraph:
- ChatGoogleGenerativeAI for the LLM
- @tool decorator from langchain_core for custom tools
- langgraph.prebuilt.create_react_agent for the agent loop
- Token counts from usage_metadata on AIMessage objects
"""

import time
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool as lc_tool
from langgraph.prebuilt import create_react_agent

from .config import MODEL, GOOGLE_API_KEY, NUM_RUNS
from .tasks import (
    TASK1_PROMPT, TASK2_PROMPT, TASK3_PROMPT, TASK4_PROMPT,
    _categorize_logic, _calc_roi_logic, _exec_summary_logic,
    _analyze_headcount_logic, _workforce_report_logic,
    _sort_tickets_logic, _action_plan_logic,
)
from .results import RunResult, estimate_cost

LIBRARY = "LangChain"


def _make_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=MODEL, google_api_key=GOOGLE_API_KEY, temperature=0)


def _j(v):
    """Parse a tool argument that may be a JSON string or already a Python object."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


# ─── Tool definitions ──────────────────────────────────────────

@lc_tool
def categorize_expenses(expenses_json: str) -> str:
    """Categorize a list of expense items by type and compute totals.
    Input: JSON array of objects with 'description' (str) and 'amount' (float) fields."""
    return json.dumps(_categorize_logic(_j(expenses_json)))


@lc_tool
def calculate_quarterly_roi(quarters_json: str) -> str:
    """Calculate ROI (revenue / marketing spend) per quarter.
    Input: JSON array with 'quarter', 'revenue', 'marketing' fields."""
    return json.dumps(_calc_roi_logic(_j(quarters_json)))


@lc_tool
def generate_executive_summary(roi_data_json: str) -> str:
    """Generate a board-ready executive summary paragraph from quarterly ROI data.
    Input: JSON array returned by calculate_quarterly_roi (must contain 'roi' field per item)."""
    data = _j(roi_data_json)
    if not isinstance(data, list):
        data = _j(str(data))
    return _exec_summary_logic(data)


@lc_tool
def analyze_headcount(departments_json: str) -> str:
    """Analyse headcount per department.
    Input: JSON object mapping department name to list of [name, level] pairs."""
    return json.dumps(_analyze_headcount_logic(_j(departments_json)))


@lc_tool
def generate_workforce_report(stats_json: str) -> str:
    """Generate a formatted HR workforce distribution report.
    Input: JSON object returned by analyze_headcount."""
    return _workforce_report_logic(_j(stats_json))


@lc_tool
def parse_and_sort_tickets(tickets_json: str) -> str:
    """Parse and sort IT support tickets by severity (critical → high → low).
    Input: JSON array with 'id', 'description', 'severity' fields."""
    return json.dumps(_sort_tickets_logic(_j(tickets_json)))


@lc_tool
def generate_action_plan(sorted_tickets_json: str) -> str:
    """Generate a prioritised IT action plan from sorted tickets.
    Input: JSON array returned by parse_and_sort_tickets."""
    return _action_plan_logic(_j(sorted_tickets_json))


# ─── Runner ───────────────────────────────────────────────────

def _extract_answer(output: dict) -> str:
    msgs = output.get("messages", [])
    if not msgs:
        return ""
    last = msgs[-1]
    if hasattr(last, "content"):
        return str(last.content)
    return str(last)


def _run(task_id: int, task_name: str, prompt: str, tools: list, run_number: int) -> RunResult:
    try:
        llm = _make_llm()
        agent = create_react_agent(llm, tools)

        t0 = time.perf_counter()
        output = agent.invoke({
            "messages": [
                ("system", "You are a helpful business assistant. Use the available tools to complete the task accurately."),
                ("human", prompt),
            ]
        })
        duration_ms = int((time.perf_counter() - t0) * 1000)

        answer = _extract_answer(output)

        input_tokens = output_tokens = cost = None
        try:
            for msg in output.get("messages", []):
                um = getattr(msg, "usage_metadata", None)
                if um:
                    if isinstance(um, dict):
                        input_tokens = (input_tokens or 0) + um.get("input_tokens", 0)
                        output_tokens = (output_tokens or 0) + um.get("output_tokens", 0)
                    else:
                        input_tokens = (input_tokens or 0) + getattr(um, "input_tokens", 0)
                        output_tokens = (output_tokens or 0) + getattr(um, "output_tokens", 0)
            if input_tokens and output_tokens:
                cost = estimate_cost(input_tokens, output_tokens)
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
