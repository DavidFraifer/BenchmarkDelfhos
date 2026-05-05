"""
Task definitions for the benchmark.

4 realistic company-environment tasks:
  1. Expense Categorisation     – single custom tool
  2. Quarterly ROI Analysis     – two chained custom tools
  3. HR Headcount Report        – two chained custom tools
  4. IT Ticket Prioritisation   – two chained custom tools

Each task is characterised by a PROMPT and shared pure-Python logic used by all
runners so the tool *behaviour* is identical across libraries.
"""

import json

# ──────────────────────────────────────────────────────────────
# Task 1 — Expense Categorisation
# ──────────────────────────────────────────────────────────────

TASK1_NAME = "Expense Categorisation"
TASK1_PROMPT = (
    "Our team submitted the following expenses this week:\n"
    "- Uber to client meeting: $67\n"
    "- AWS cloud hosting: $299\n"
    "- Team lunch with client: $187\n"
    "- Microsoft 365 subscription: $150\n"
    "- Flight to NYC: $420\n"
    "- Office supplies: $89\n"
    "- Zoom Pro subscription: $149\n"
    "- Coffee meeting: $45\n\n"
    "Use the categorize_expenses tool. "
    "Pass ALL 8 expenses as a JSON array where each object has exactly two keys: "
    "'description' (string) and 'amount' (number). "
    "Example: [{\"description\": \"Uber to airport\", \"amount\": 67}]. "
    "After calling the tool, report the total per category and the grand total."
)

_CATEGORY_KEYWORDS = {
    "uber": "Travel", "flight": "Travel", "taxi": "Travel", "train": "Travel",
    "lunch": "Food", "dinner": "Food", "coffee": "Food", "breakfast": "Food",
    "aws": "Software", "azure": "Software", "microsoft": "Software",
    "zoom": "Software", "subscription": "Software", "saas": "Software",
    "office": "Office", "supplies": "Office", "stationery": "Office",
}


def _categorize_logic(items: list) -> dict:
    """Pure-Python implementation shared by all libraries.
    Accepts each item as a dict {'description': str, 'amount': float}
    OR as a string 'description: $amount' OR 'description ($amount)'."""
    import re
    totals: dict[str, float] = {"Travel": 0.0, "Food": 0.0, "Software": 0.0, "Office": 0.0, "Other": 0.0}
    detail = []
    for item in items:
        if isinstance(item, dict):
            desc = str(item.get("description", item.get("name", item.get("item", "")))).lower()
            amount = float(item.get("amount", item.get("cost", item.get("price", 0))))
            desc_display = item.get("description", item.get("name", str(item)))
        else:
            raw = str(item)
            m = re.search(r"\$?([\d,]+(?:\.\d+)?)", raw)
            amount = float(m.group(1).replace(",", "")) if m else 0.0
            desc = raw.lower()
            desc_display = raw
        cat = next((c for kw, c in _CATEGORY_KEYWORDS.items() if kw in desc), "Other")
        totals[cat] += amount
        detail.append({"description": desc_display, "amount": amount, "category": cat})
    totals["Grand Total"] = sum(v for k, v in totals.items() if k != "Grand Total")
    return {"items": detail, "totals": totals}


# ──────────────────────────────────────────────────────────────
# Task 2 — Quarterly ROI Analysis (two tools chained)
# ──────────────────────────────────────────────────────────────

TASK2_NAME = "Quarterly ROI Analysis"
TASK2_PROMPT = (
    "We have the following quarterly data:\n"
    "Q1: Revenue=$145,000 | Marketing=$20,000\n"
    "Q2: Revenue=$168,000 | Marketing=$25,000\n"
    "Q3: Revenue=$152,000 | Marketing=$22,000\n"
    "Q4: Revenue=$195,000 | Marketing=$30,000\n\n"
    "Step 1 – call calculate_quarterly_roi with a list of 4 dicts, each having "
    "'quarter' (string), 'revenue' (number), 'marketing' (number). "
    'Example input: [{"quarter":"Q1","revenue":145000,"marketing":20000}, ...].\n'
    "Step 2 – read the ROI values from the tool output, then call generate_executive_summary "
    "passing the best_quarter name, worst_quarter name, their ROI values, and the average ROI "
    "to produce a board-ready paragraph."
)

_QUARTERLY_DATA = [
    {"quarter": "Q1", "revenue": 145000, "marketing": 20000},
    {"quarter": "Q2", "revenue": 168000, "marketing": 25000},
    {"quarter": "Q3", "revenue": 152000, "marketing": 22000},
    {"quarter": "Q4", "revenue": 195000, "marketing": 30000},
]


def _calc_roi_logic(quarters: list) -> list:
    return [
        {**q, "roi": round(q["revenue"] / q["marketing"], 2)}
        for q in quarters
    ]


def _exec_summary_logic(roi_data) -> str:
    if isinstance(roi_data, str) or not isinstance(roi_data, list) or not roi_data:
        return ("Executive Summary: The company's quarterly marketing ROI analysis indicates "
                "generally solid performance across all measured periods. "
                "Detailed figures were unavailable for automatic extraction.")
    try:
        valid = [x for x in roi_data if isinstance(x, dict) and "roi" in x]
        if not valid:
            return "Executive Summary: ROI data could not be parsed from the provided results."
        best = max(valid, key=lambda x: x["roi"])
        worst = min(valid, key=lambda x: x["roi"])
        avg = round(sum(x["roi"] for x in valid) / len(valid), 2)
        return (
            f"Executive Summary: The company achieved an average marketing ROI of {avg}x "
            f"across all measured quarters. {best['quarter']} delivered the strongest return "
            f"({best['roi']}x), while {worst['quarter']} was the weakest ({worst['roi']}x). "
            f"The overall trend shows solid and improving marketing efficiency, positioning "
            f"the business well for continued growth."
        )
    except Exception:
        return "Executive Summary: Unable to generate summary from provided ROI data."


# ──────────────────────────────────────────────────────────────
# Task 3 — HR Headcount Report (two tools chained)
# ──────────────────────────────────────────────────────────────

TASK3_NAME = "HR Headcount Report"
TASK3_PROMPT = (
    "Here is our current employee roster:\n"
    "Engineering: Alice (Senior), Bob (Senior), Carol (Senior), David (Senior), Eve (Junior)\n"
    "Sales: Frank (Senior), Grace (Junior), Hank (Junior)\n"
    "Marketing: Ivy (Senior), Jack (Junior), Kate (Senior), Liam (Junior)\n"
    "Support: Mia (Junior), Noah (Junior)\n\n"
    "Step 1 – call analyze_headcount with a dict where each key is a department name "
    "and the value is a list of [name, level] pairs. "
    'Example: {"Engineering": [["Alice","Senior"],["Eve","Junior"]], "Sales": [...]}.\n'
    "Step 2 – from the tool output, identify the largest dept, smallest dept, total employees, "
    "and senior/junior counts, then call generate_workforce_report with those values "
    "to produce a formatted HR report."
)

_ROSTER = {
    "Engineering": [("Alice", "Senior"), ("Bob", "Senior"), ("Carol", "Senior"), ("David", "Senior"), ("Eve", "Junior")],
    "Sales": [("Frank", "Senior"), ("Grace", "Junior"), ("Hank", "Junior")],
    "Marketing": [("Ivy", "Senior"), ("Jack", "Junior"), ("Kate", "Senior"), ("Liam", "Junior")],
    "Support": [("Mia", "Junior"), ("Noah", "Junior")],
}


def _analyze_headcount_logic(departments: dict) -> dict:
    stats = {}
    for dept, members in departments.items():
        seniors = 0
        total = 0
        for m in members:
            total += 1
            if isinstance(m, dict):
                level = str(m.get("level", m.get("seniority", "")))
            elif isinstance(m, (list, tuple)) and len(m) >= 2:
                level = str(m[1])
            else:
                level = str(m)
            if level.lower() in ("senior", "sr"):
                seniors += 1
        stats[dept] = {"total": total, "senior": seniors, "junior": total - seniors}
    return stats


def _workforce_report_logic(stats) -> str:
    if isinstance(stats, str):
        import re
        m = re.search(r'\{.*\}', stats, re.DOTALL)
        if m:
            try:
                import json as _json
                stats = _json.loads(m.group())
            except Exception:
                pass
    if not isinstance(stats, dict) or not stats:
        return "Workforce report unavailable: stats data not in expected format."
    clean = {}
    for dept, v in stats.items():
        if isinstance(v, dict):
            clean[dept] = v
        elif isinstance(v, (int, float)):
            clean[dept] = {"total": int(v), "senior": 0, "junior": int(v)}
    if not clean:
        return "Workforce report unavailable: could not parse department stats."
    largest = max(clean, key=lambda d: clean[d].get("total", 0))
    smallest = min(clean, key=lambda d: clean[d].get("total", 0))
    total_emp = sum(s.get("total", 0) for s in clean.values())
    total_senior = sum(s.get("senior", 0) for s in clean.values())
    total_junior = sum(s.get("junior", 0) for s in clean.values())
    lines = [
        "=== Workforce Distribution Report ===",
        f"Total Employees: {total_emp}",
        f"Senior / Junior: {total_senior} / {total_junior} "
        f"({round(total_senior / total_emp * 100) if total_emp else 0}% / "
        f"{round(total_junior / total_emp * 100) if total_emp else 0}%)",
        f"Largest Department: {largest} ({clean[largest].get('total', 0)} people)",
        f"Smallest Department: {smallest} ({clean[smallest].get('total', 0)} people)",
        "",
        "Department Breakdown:",
    ]
    for dept, s in sorted(clean.items(), key=lambda x: -x[1].get("total", 0)):
        lines.append(f"  {dept:15s} {s.get('total',0)} total  "
                     f"({s.get('senior',0)} senior, {s.get('junior',0)} junior)")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Task 4 — IT Ticket Prioritisation (two tools chained)
# ──────────────────────────────────────────────────────────────

TASK4_NAME = "IT Ticket Prioritisation"
TASK4_PROMPT = (
    "The following IT support tickets were submitted today:\n"
    "T001 | Production server down (all services unreachable) | critical\n"
    "T002 | Laptop keyboard not working – employee can use external keyboard | low\n"
    "T003 | VPN broken for all 45 remote employees | high\n"
    "T004 | Outlook email signature missing | low\n"
    "T005 | Nightly database backup failed – last successful backup 48 h ago | high\n"
    "T006 | CEO cannot access email on mobile | critical\n"
    "T007 | Printer on floor 3 offline | low\n"
    "T008 | Security patch deployment required on 200 endpoints | high\n\n"
    "Step 1 – call parse_and_sort_tickets with a list of 8 ticket dicts, "
    'each having "id" (string), "description" (string), "severity" (critical/high/low). '
    'Example: [{"id":"T001","description":"Server down","severity":"critical"}, ...].\n'
    "Step 2 – pass the sorted output string to generate_action_plan to produce a "
    "prioritised action plan with response-time targets for the IT team."
)

_TICKETS_RAW = [
    {"id": "T001", "description": "Production server down (all services unreachable)", "severity": "critical"},
    {"id": "T002", "description": "Laptop keyboard not working – employee can use external keyboard", "severity": "low"},
    {"id": "T003", "description": "VPN broken for all 45 remote employees", "severity": "high"},
    {"id": "T004", "description": "Outlook email signature missing", "severity": "low"},
    {"id": "T005", "description": "Nightly database backup failed – last successful backup 48 h ago", "severity": "high"},
    {"id": "T006", "description": "CEO cannot access email on mobile", "severity": "critical"},
    {"id": "T007", "description": "Printer on floor 3 offline", "severity": "low"},
    {"id": "T008", "description": "Security patch deployment required on 200 endpoints", "severity": "high"},
]

_SEVERITY_ORDER = {"critical": 0, "high": 1, "low": 2}
_RESPONSE_TIME = {"critical": "Immediate (< 15 min)", "high": "Within 2 hours", "low": "Within 24 hours"}


def _sort_tickets_logic(tickets: list) -> list:
    return sorted(tickets, key=lambda t: (_SEVERITY_ORDER.get(t.get("severity", "low"), 2), t.get("id", "")))


def _action_plan_logic(sorted_tickets: list) -> str:
    lines = ["=== IT Action Plan ===", ""]
    current_sev = None
    for t in sorted_tickets:
        sev = t.get("severity", "low")
        if sev != current_sev:
            lines.append(f"[{sev.upper()}]")
            current_sev = sev
        rt = _RESPONSE_TIME.get(sev, "TBD")
        lines.append(f"  {t['id']} – {t['description']}")
        lines.append(f"       Response: {rt}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Convenience: list of all tasks
# ──────────────────────────────────────────────────────────────

ALL_TASKS = [
    {"id": 1, "name": TASK1_NAME, "prompt": TASK1_PROMPT},
    {"id": 2, "name": TASK2_NAME, "prompt": TASK2_PROMPT},
    {"id": 3, "name": TASK3_NAME, "prompt": TASK3_PROMPT},
    {"id": 4, "name": TASK4_NAME, "prompt": TASK4_PROMPT},
]
