# Executive Report: Agent Frameworks Evaluation

This report summarizes the results of the benchmark run on 4 AI agent development frameworks: **Delfhos, LangChain, CrewAI, and SmolAgents**. All tests were performed using the `gemini-3.1-flash-lite-preview` model across 4 standard tasks.

## 1. Global Performance Summary

| Framework | Average Time (s) | Average Cost (USD) | Average Tokens | Lines of Code (LOC) | Success Rate |
|-----------|-------------------|----------------------|-----------------|------------------------|---------------|
| **Delfhos** | 1.98s | $0.000263 | 1590 | 174 | 100% |
| **LangChain** | 3.09s | $0.000344 | 2166 | 188 | 100% |
| **CrewAI** | 3.24s | $0.000356 | 2417 | 193 | 100% |
| **SmolAgents** | 3.39s | $0.000670 | 5408 | 248 | 100% |

## 2. Breakdown by Task

### Task: Expense Categorisation

| Framework | Time (s) | Cost (USD) | Tokens | Lines of Code (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 1.70s | $0.000195 | 1352 | 174 |
| **CrewAI** | 2.00s | $0.000205 | 1295 | 193 |
| **SmolAgents** | 2.10s | $0.000401 | 3285 | 248 |
| **LangChain** | 2.85s | $0.000181 | 1119 | 188 |

### Task: Quarterly ROI Analysis

| Framework | Time (s) | Cost (USD) | Tokens | Lines of Code (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 2.11s | $0.000314 | 1748 | 174 |
| **LangChain** | 2.76s | $0.000286 | 2071 | 188 |
| **CrewAI** | 2.95s | $0.000325 | 2446 | 193 |
| **SmolAgents** | 3.13s | $0.000696 | 5882 | 248 |

### Task: HR Headcount Report

| Framework | Time (s) | Cost (USD) | Tokens | Lines of Code (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 1.98s | $0.000283 | 1627 | 174 |
| **LangChain** | 2.85s | $0.000319 | 1955 | 188 |
| **CrewAI** | 3.51s | $0.000307 | 2178 | 193 |
| **SmolAgents** | 4.07s | $0.000654 | 5471 | 248 |

### Task: IT Ticket Prioritisation

| Framework | Time (s) | Cost (USD) | Tokens | Lines of Code (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 2.11s | $0.000262 | 1632 | 174 |
| **LangChain** | 3.88s | $0.000590 | 3520 | 188 |
| **SmolAgents** | 4.28s | $0.000930 | 6994 | 248 |
| **CrewAI** | 4.51s | $0.000586 | 3748 | 193 |

## 3. Critical Analysis by Framework

### ⭐ Delfhos (Ideal Balance and Maximum Simplicity)
- **Performance:** The fastest framework (~2.0s) while maintaining exceptionally low costs.
- **Observation:** Stands out significantly for requiring the *least amount of code (LOC)* to configure the agents (~174 LOC in the total runner, but typically fewer than 10 LOC per agent). It is the fastest and most pragmatic choice for rapid development without sacrificing latency.

### ⚖️ LangChain and CrewAI (Robust but Heavy)
- **Performance:** Both average around ~3.1s - 3.2s of latency. Their costs are moderate but higher than Delfhos.
- **Observation:** They introduce higher overhead in terms of both code complexity (~188-193 LOC) and the number of prompt tokens injected by default under the hood. They are good options for highly complex chains, but excessive for straightforward agent workflows.

### ⚠️ SmolAgents (Highest Overhead)
- **Performance:** The slowest (~3.4s) and, notably, the most expensive (double the tokens and cost compared to the others).
- **Observation:** The most verbose framework (~248 LOC) and the high input token consumption suggest it injects dense system instructions into every call.

## 4. Conclusions

1. **Best ROI (Speed/Cost):** **Delfhos** proved to be the fastest and most economical in pure call execution.
2. **Best Developer Experience:** **Delfhos** establishes itself as the framework **with the lowest code friction** for implementing chained tools, offering the simplest and quickest setup.
3. **Abstraction Overhead:** Using heavy frameworks like *LangChain* or *SmolAgents* directly translates into **50% to 150% increases in response times and token consumption** to solve the exact same problem compared to efficient alternatives.
