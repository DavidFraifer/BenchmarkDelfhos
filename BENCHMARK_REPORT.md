# Agent Framework Benchmark Report

**Date:** 2026-06-17 19:00 UTC  
**Model:** `gemini-3.1-flash-lite-preview`  
**Runs per task:** 3  
**Libraries:** Delfhos, LangChain, SmolAgents  

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
| Delfhos | 100% | 1.5s | 1154 | 198 | $0.00019 | 8 |
| LangChain | 100% | 1.7s | 888 | 231 | $0.00018 | 15 |
| SmolAgents | 100% | 1.7s | 3041 | 232 | $0.00040 | 10 |


## Task 2: Quarterly ROI Analysis

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | 100% | 2.0s | 1283 | 468 | $0.00032 | 9 |
| LangChain | 100% | 2.2s | 1808 | 263 | $0.00029 | 16 |
| SmolAgents | 100% | 2.4s | 5525 | 367 | $0.00070 | 11 |


## Task 3: HR Headcount Report

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | 100% | 1.8s | 1227 | 404 | $0.00028 | 9 |
| LangChain | 100% | 2.6s | 1542 | 414 | $0.00032 | 16 |
| SmolAgents | 100% | 2.3s | 5099 | 328 | $0.00064 | 11 |


## Task 4: IT Ticket Prioritisation

| Library | Success Rate | Avg Time | Avg Input Tok | Avg Output Tok | Avg Cost | Setup LOC |
|---------|-------------|----------|---------------|----------------|----------|-----------|
| Delfhos | 100% | 1.6s | 1303 | 329 | $0.00026 | 9 |
| LangChain | 100% | 3.5s | 2727 | 793 | $0.00059 | 16 |
| SmolAgents | 100% | 3.4s | 6221 | 768 | $0.00093 | 11 |


---

## Overall Summary

| Library | Avg Success | Avg Time | Total Cost | Avg Setup LOC |
|---------|------------|----------|------------|---------------|
| Delfhos | 100% | 1.7s | $0.00317 | 9 |
| LangChain | 100% | 2.5s | $0.00413 | 16 |
| SmolAgents | 100% | 2.5s | $0.00800 | 11 |

---

## Notes

- **Setup LOC** counts non-blank, non-comment lines required to initialise the agent and define tools for a single task (imports excluded).
- **Token counts** are extracted from each framework's native usage tracking: Delfhos (built-in), LangChain (`usage_metadata` per `AIMessage`), SmolAgents (`agent.monitor.get_total_token_counts()`).
- Each task was run 3 times; averages are taken over successful runs only.