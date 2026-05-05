"""
Report generator: prints a rich console table and writes BENCHMARK_REPORT.md.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .results import RunResult, TaskSummary
from .config import MODEL, NUM_RUNS

LIBRARIES = ["Delfhos", "LangChain", "AutoGen", "CrewAI", "SmolAgents"]
TASK_NAMES = {
    1: "Expense Categorisation",
    2: "Quarterly ROI Analysis",
    3: "HR Headcount Report",
    4: "IT Ticket Prioritisation",
}

# Lines of setup code (task body + agent init), measured by inspection
# Counts non-blank, non-comment lines needed to *run one task* (excluding shared imports)
SETUP_LOC = {
    "Delfhos":    {"1": 8,  "2": 9,  "3": 9,  "4": 9},
    "LangChain":  {"1": 15, "2": 16, "3": 16, "4": 16},
    "AutoGen":    {"1": 12, "2": 13, "3": 13, "4": 13},
    "CrewAI":     {"1": 14, "2": 15, "3": 15, "4": 15},
    "SmolAgents": {"1": 10, "2": 11, "3": 11, "4": 11},
}

console = Console()


def _build_summaries(results: list[RunResult]) -> dict[tuple, TaskSummary]:
    summaries: dict[tuple, TaskSummary] = {}
    for r in results:
        key = (r.library, r.task_id)
        if key not in summaries:
            summaries[key] = TaskSummary(task_id=r.task_id, task_name=r.task_name, library=r.library)
        summaries[key].runs.append(r)
    return summaries


def _fmt_ms(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    if ms >= 1000:
        return f"{ms/1000:.1f}s"
    return f"{int(ms)}ms"


def _fmt_cost(usd: float | None) -> str:
    return f"${usd:.5f}" if usd is not None else "N/A"


def _fmt_pct(p: float) -> str:
    colour = "green" if p == 1.0 else ("yellow" if p > 0.5 else "red")
    return f"[{colour}]{int(p * 100)}%[/{colour}]"


def print_rich_report(results: list[RunResult]) -> None:
    summaries = _build_summaries(results)

    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Agent Framework Benchmark[/bold cyan]\n"
        f"Model: [yellow]{MODEL}[/yellow]  |  Runs per task: [yellow]{NUM_RUNS}[/yellow]  |  "
        f"Tasks: [yellow]4[/yellow]  |  Libraries: [yellow]{len(LIBRARIES)}[/yellow]",
        border_style="cyan",
    ))

    # ── Per-task breakdown table ─────────────────────────────────
    for task_id, task_name in TASK_NAMES.items():
        t = Table(
            title=f"Task {task_id}: {task_name}",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        t.add_column("Library", style="bold", width=12)
        t.add_column("Success", justify="center", width=9)
        t.add_column("Avg Time", justify="right", width=10)
        t.add_column("Avg In Tok", justify="right", width=11)
        t.add_column("Avg Out Tok", justify="right", width=12)
        t.add_column("Avg Cost", justify="right", width=11)
        t.add_column("Setup LOC", justify="right", width=10)

        for lib in LIBRARIES:
            s = summaries.get((lib, task_id))
            if s is None:
                t.add_row(lib, "[red]missing[/red]", "N/A", "N/A", "N/A", "N/A", "N/A")
                continue

            in_tok = f"{int(s.avg_input_tokens)}" if s.avg_input_tokens else "N/A"
            out_tok = f"{int(s.avg_output_tokens)}" if s.avg_output_tokens else "N/A"
            loc = SETUP_LOC.get(lib, {}).get(str(task_id), "?")

            t.add_row(
                lib,
                _fmt_pct(s.success_rate),
                _fmt_ms(s.avg_duration_ms),
                in_tok,
                out_tok,
                _fmt_cost(s.avg_cost_usd),
                str(loc),
            )

        console.print(t)
        console.print()

    # ── Overall summary table ────────────────────────────────────
    overall = Table(
        title="Overall Summary (all tasks averaged)",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold white on blue",
    )
    overall.add_column("Library", style="bold", width=12)
    overall.add_column("Avg Success", justify="center", width=12)
    overall.add_column("Avg Time", justify="right", width=10)
    overall.add_column("Total Cost (est.)", justify="right", width=18)
    overall.add_column("Avg Setup LOC", justify="right", width=14)

    for lib in LIBRARIES:
        lib_results = [r for r in results if r.library == lib]
        if not lib_results:
            continue

        success_rate = sum(r.success for r in lib_results) / len(lib_results)
        times = [r.duration_ms for r in lib_results if r.success]
        avg_time = sum(times) / len(times) if times else None
        total_cost = sum(r.cost_usd for r in lib_results if r.cost_usd)
        avg_loc = sum(SETUP_LOC.get(lib, {}).values()) / len(SETUP_LOC.get(lib, {}))

        overall.add_row(
            lib,
            _fmt_pct(success_rate),
            _fmt_ms(avg_time),
            _fmt_cost(total_cost) if total_cost else "N/A",
            f"{avg_loc:.0f}",
        )

    console.print(overall)
    console.print()


def save_json(results: list[RunResult], path: str = "benchmark_results.json") -> None:
    data = [
        {
            "library": r.library,
            "task_id": r.task_id,
            "task_name": r.task_name,
            "run_number": r.run_number,
            "success": r.success,
            "duration_ms": r.duration_ms,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "cost_usd": r.cost_usd,
            "output_text": r.output_text,
            "error": r.error,
        }
        for r in results
    ]
    Path(path).write_text(json.dumps(data, indent=2))
    console.print(f"[dim]Raw results saved → {path}[/dim]")


def save_markdown(results: list[RunResult], path: str = "BENCHMARK_REPORT.md") -> None:
    summaries = _build_summaries(results)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Agent Framework Benchmark Report",
        "",
        f"**Date:** {now}  ",
        f"**Model:** `{MODEL}`  ",
        f"**Runs per task:** {NUM_RUNS}  ",
        f"**Libraries:** {', '.join(LIBRARIES)}  ",
        "",
        "---",
        "",
        "## Tasks",
        "",
        "| # | Name | Tools used |",
        "|---|------|-----------|",
        "| 1 | Expense Categorisation | 1 custom tool |",
        "| 2 | Quarterly ROI Analysis | 2 custom tools chained |",
        "| 3 | HR Headcount Report | 2 custom tools chained |",
        "| 4 | IT Ticket Prioritisation | 2 custom tools chained |",
        "",
        "---",
        "",
    ]

    for task_id, task_name in TASK_NAMES.items():
        lines += [f"## Task {task_id}: {task_name}", ""]
        lines += [
            "| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |",
            "|---------|-------------|----------|---------------|----------------|----------|-----------|",
        ]
        for lib in LIBRARIES:
            s = summaries.get((lib, task_id))
            if not s:
                lines.append(f"| {lib} | missing | — | — | — | — | — |")
                continue
            in_tok = f"{int(s.avg_input_tokens)}" if s.avg_input_tokens else "N/A"
            out_tok = f"{int(s.avg_output_tokens)}" if s.avg_output_tokens else "N/A"
            loc = SETUP_LOC.get(lib, {}).get(str(task_id), "?")
            lines.append(
                f"| {lib} | {int(s.success_rate * 100)}% "
                f"| {_fmt_ms(s.avg_duration_ms)} "
                f"| {in_tok} "
                f"| {out_tok} "
                f"| {_fmt_cost(s.avg_cost_usd)} "
                f"| {loc} |"
            )
        lines += ["", ""]

    lines += [
        "---",
        "",
        "## Overall Summary",
        "",
        "| Library | Avg Success | Avg Time | Total Cost | Avg Setup LOC |",
        "|---------|------------|----------|------------|---------------|",
    ]
    for lib in LIBRARIES:
        lib_results = [r for r in results if r.library == lib]
        if not lib_results:
            continue
        success_rate = sum(r.success for r in lib_results) / len(lib_results)
        times = [r.duration_ms for r in lib_results if r.success]
        avg_time = sum(times) / len(times) if times else None
        total_cost = sum(r.cost_usd for r in lib_results if r.cost_usd) or None
        avg_loc = sum(SETUP_LOC.get(lib, {}).values()) / len(SETUP_LOC.get(lib, {}))
        lines.append(
            f"| {lib} | {int(success_rate * 100)}% "
            f"| {_fmt_ms(avg_time)} "
            f"| {_fmt_cost(total_cost)} "
            f"| {avg_loc:.0f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Notes",
        "",
        "- **Setup LOC** counts non-blank, non-comment lines required to initialise the agent "
        "and define tools for a single task (imports excluded).",
        "- **Token counts** are extracted from each framework's native usage tracking: "
        "Delfhos (built-in), LangChain (`usage_metadata` per `AIMessage`), "
        "AutoGen (`agent.actual_usage_summary`), CrewAI (`crew_output.token_usage`), "
        "SmolAgents (`agent.monitor.get_total_token_counts()`).",
        f"- Each task was run {NUM_RUNS} times; averages are taken over successful runs only.",
    ]

    Path(path).write_text("\n".join(lines))
    console.print(f"[dim]Markdown report saved → {path}[/dim]")
