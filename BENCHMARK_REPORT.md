# Agent Framework Benchmark Report

**Date:** 2026-06-17 18:47 UTC  
**Model:** `gemini-3.1-flash-lite-preview`  
**Runs per task:** 3  
**Libraries:** Delfhos, LangChain, AutoGen, CrewAI, SmolAgents  

---

## Tasks

| # | Name | Tools used |
|---|------|-----------|
| 1 | Expense Categorisation | 1 custom tool |
| 2 | Quarterly ROI Analysis | 2 custom tools chained |
| 3 | HR Headcount Report | 2 custom tools chained |
| 4 | IT Ticket Prioritisation | 2 custom tools chained |

---

## Task 1: Expense Categorisation

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | 100% | 1.6s | 1154 | 198 | $0.00019 | 8 |
| LangChain | missing | — | — | — | — | — |
| AutoGen | missing | — | — | — | — | — |
| CrewAI | missing | — | — | — | — | — |
| SmolAgents | missing | — | — | — | — | — |


## Task 2: Quarterly ROI Analysis

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | missing | — | — | — | — | — |
| LangChain | missing | — | — | — | — | — |
| AutoGen | missing | — | — | — | — | — |
| CrewAI | missing | — | — | — | — | — |
| SmolAgents | missing | — | — | — | — | — |


## Task 3: HR Headcount Report

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | missing | — | — | — | — | — |
| LangChain | missing | — | — | — | — | — |
| AutoGen | missing | — | — | — | — | — |
| CrewAI | missing | — | — | — | — | — |
| SmolAgents | missing | — | — | — | — | — |


## Task 4: IT Ticket Prioritisation

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | missing | — | — | — | — | — |
| LangChain | missing | — | — | — | — | — |
| AutoGen | missing | — | — | — | — | — |
| CrewAI | missing | — | — | — | — | — |
| SmolAgents | missing | — | — | — | — | — |


---

## Overall Summary

| Library | Avg Success | Avg Time | Total Cost | Avg Setup LOC |
|---------|------------|----------|------------|---------------|
| Delfhos | 100% | 1.6s | $0.00058 | 9 |

---

## Notes

- **Setup LOC** counts non-blank, non-comment lines required to initialise the agent and define tools for a single task (imports excluded).
- **Token counts** are extracted from each framework's native usage tracking: Delfhos (built-in), LangChain (`usage_metadata` per `AIMessage`), AutoGen (`agent.actual_usage_summary`), CrewAI (`crew_output.token_usage`), SmolAgents (`agent.monitor.get_total_token_counts()`).
- Each task was run 3 times; averages are taken over successful runs only.