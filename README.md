# Agent Framework Benchmark

A comprehensive, professional benchmarking suite designed to compare modern LLM agent frameworks on standard business-oriented tool-calling tasks. The benchmark evaluates performance across multiple dimensions: **execution speed (latency)**, **token usage (input & output)**, **API cost**, and **developer experience (Lines of Code)**.

---

## 🚀 Overview

This repository benchmarks 3 prominent agent frameworks using Google Gemini (`gemini-3.1-flash-lite-preview` by default):

1. **Delfhos**: A lightweight, high-performance agent framework focused on simplicity and minimal developer overhead.
2. **LangChain** (with LangGraph): The industry-standard framework for building complex, graph-based agent topologies.
3. **SmolAgents**: Hugging Face's minimalist library for code-agent and tool-calling flows.

---

## 📋 Tasks

The benchmark evaluates each framework across 4 realistic business tasks, using identical tool-execution logic to isolate the overhead of each framework's orchestration loop:

1. **Expense Categorisation** *(Single custom tool)*
   - Processes a list of raw expenses, categorizes them using pre-defined rules, and generates a formatted total report.
2. **Quarterly ROI Analysis** *(Two custom tools chained)*
   - Calculates marketing ROI across multiple quarters and feeds the output directly into a second summarization tool.
3. **HR Headcount Report** *(Two custom tools chained)*
   - Analyzes employee seniority distributions per department and generates a formatted corporate workforce report.
4. **IT Ticket Prioritisation** *(Two custom tools chained)*
   - Sorts incoming support tickets by severity (critical, high, low) and creates a priority-based action plan with response-time targets.

---

## 📊 Key Benchmark Metrics

- **Success Rate**: The percentage of runs that completed successfully without agent loop crashes or tool-calling failure.
- **Latency (Avg Time)**: Total round-trip execution time in seconds.
- **Token Count**: Input and output token quantities parsed directly from each framework's native tracking APIs.
- **Cost (USD)**: Calculated based on token prices (input and output) for `gemini-3.1-flash-lite-preview`.
- **Setup LOC (Lines of Code)**: The number of lines required to define the tools, initialize the agent, and kick off the task for comparison.

For detailed results, see [benchmark_report_analysis.md](benchmark_report_analysis.md).

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10 or higher.
- A Google Gemini API key.

### 2. Install Dependencies
Clone the repository and install the framework-specific packages using pip:

```bash
pip install -r requirements_benchmark.txt
```

### 3. Environment Configuration
Create a `.env` file in the root of the project (you can copy `.env.example` as a template) and add your API key:

```bash
cp .env.example .env
```

Open `.env` and configure:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## 🏃 Run the Benchmark

You can run the entire benchmark suite or target specific frameworks and tasks.

### Run all libraries and tasks (3 iterations each)
```bash
python run_benchmark.py
```

### Run specific libraries
```bash
python run_benchmark.py --libs delfhos langchain
```

### Run specific tasks
```bash
python run_benchmark.py --tasks 1 3
```

### Command Line Options
```text
options:
  -h, --help           show this help message and exit
  --libs LIBS [LIBS ...]
                       Libraries to benchmark (choices: delfhos, langchain, smolagents)
                       Default: runs all libraries
  --tasks TASKS [TASKS ...]
                       Task IDs to run (choices: 1, 2, 3, 4)
                       Default: runs all tasks
```

---

## 📝 Outputs & Reports

Every completed benchmark run produces the following output files:

1. **Terminal Console Report**: A beautiful, color-coded tables summary printed via the `rich` library.
2. **Raw JSON Logs (`benchmark_results.json`)**: Full execution metadata (durations, success status, token count, cost, output snippets, errors) for further analysis.
3. **Markdown Report (`BENCHMARK_REPORT.md`)**: A structured markdown table summarizing results by task and overall average, perfect for sharing.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
