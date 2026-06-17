#!/usr/bin/env python3
"""
run_benchmark.py — Main entry point for the agent framework benchmark.

Usage:
    python run_benchmark.py                            # Run all libraries
    python run_benchmark.py --libs delfhos langchain   # Run specific libraries
    python run_benchmark.py --tasks 1 3               # Run specific tasks only

Libraries compared:
    Delfhos · LangChain · AutoGen · CrewAI · SmolAgents

Tasks (all using gemini-3.1-flash-lite-preview):
    1. Expense Categorisation     – single custom tool
    2. Quarterly ROI Analysis     – two chained custom tools
    3. HR Headcount Report        – two chained custom tools
    4. IT Ticket Prioritisation   – two chained custom tools
"""

import argparse
import sys
import time
import os
import warnings
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Suppress LangChain warnings regarding both keys being set
if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ.pop("GEMINI_API_KEY")
warnings.filterwarnings("ignore")

# Suppress Delfhos standard verbose output
os.environ["DELFHOS_LOG_LEVEL"] = "ERROR"

console = Console()

# ─── CLI ──────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Agent framework benchmark")
    p.add_argument(
        "--libs",
        nargs="+",
        choices=["delfhos", "langchain", "smolagents"],
        default=["delfhos", "langchain", "smolagents"],
        help="Libraries to benchmark (default: all)",
    )
    p.add_argument(
        "--tasks",
        nargs="+",
        type=int,
        choices=[1, 2, 3, 4],
        default=[1, 2, 3, 4],
        help="Task IDs to run (default: all)",
    )
    return p.parse_args()


# ─── Library runners ──────────────────────────────────────────

RUNNER_MAP = {
    "delfhos":    "benchmark.run_delfhos",
    "langchain":  "benchmark.run_langchain",
    "smolagents": "benchmark.run_smolagents",
}

DISPLAY_NAMES = {
    "delfhos":    "Delfhos",
    "langchain":  "LangChain",
    "smolagents": "SmolAgents",
}


def _import_runner(lib: str):
    import importlib
    return importlib.import_module(RUNNER_MAP[lib])


def _check_imports(libs: list[str]) -> list[str]:
    """Return list of libs with missing dependencies."""
    missing = []
    checks = {
        "langchain":  "langchain_google_genai",
        "smolagents": "smolagents",
    }
    for lib in libs:
        pkg = checks.get(lib)
        if pkg:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(lib)
    return missing


# ─── Main ─────────────────────────────────────────────────────

def main():
    args = parse_args()

    libs = args.libs
    task_filter = set(args.tasks)

    # Dependency check
    missing = _check_imports(libs)
    if missing:
        console.print(f"[red]Missing packages for: {', '.join(missing)}[/red]")
        console.print("Install with:  pip install -r requirements_benchmark.txt")
        console.print()

    all_results = []
    total_tasks = len(libs) * len(task_filter) * 3  # NUM_RUNS=3

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        bench_task = progress.add_task("[cyan]Running benchmark…", total=total_tasks)

        for lib in libs:
            if lib in missing:
                console.print(f"[red]Skipping {DISPLAY_NAMES[lib]} (missing dependency).[/red]")
                continue

            try:
                module = _import_runner(lib)
            except Exception as e:
                console.print(f"[red]Failed to import {lib}: {e}[/red]")
                continue

            progress.update(bench_task, description=f"[cyan]{DISPLAY_NAMES[lib]}…")

            try:
                import contextlib
                import io
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    results = module.run_all()
                filtered = [r for r in results if r.task_id in task_filter]
                all_results.extend(filtered)
                progress.advance(bench_task, len(filtered))
            except Exception as e:
                console.print(f"[red]{DISPLAY_NAMES[lib]} runner crashed: {e}[/red]")
                import traceback
                console.print(traceback.format_exc())

    console.print()

    if not all_results:
        console.print("[red]No results collected.[/red]")
        sys.exit(1)

    # Generate reports
    from benchmark.report import print_rich_report, save_json, save_markdown
    print_rich_report(all_results)
    save_json(all_results)
    save_markdown(all_results)

    # Quick error summary
    errors = [r for r in all_results if not r.success]
    if errors:
        console.print(f"[yellow]{len(errors)} failed run(s):[/yellow]")
        for e in errors:
            console.print(f"  [red]{e.library}[/red] task {e.task_id} run {e.run_number}: {e.error}")

    console.print("[bold green]Benchmark complete.[/bold green]")


if __name__ == "__main__":
    main()
