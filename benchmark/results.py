from dataclasses import dataclass, field
from typing import Optional
import statistics


@dataclass
class RunResult:
    task_id: int
    task_name: str
    library: str
    run_number: int
    success: bool
    duration_ms: int
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    cost_usd: Optional[float]
    output_text: str
    error: Optional[str] = None


@dataclass
class TaskSummary:
    task_id: int
    task_name: str
    library: str
    runs: list[RunResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if not self.runs:
            return 0.0
        return sum(1 for r in self.runs if r.success) / len(self.runs)

    @property
    def avg_duration_ms(self) -> Optional[float]:
        vals = [r.duration_ms for r in self.runs if r.success]
        return round(statistics.mean(vals), 0) if vals else None

    @property
    def avg_cost_usd(self) -> Optional[float]:
        vals = [r.cost_usd for r in self.runs if r.success and r.cost_usd is not None]
        return round(statistics.mean(vals), 6) if vals else None

    @property
    def avg_input_tokens(self) -> Optional[float]:
        vals = [r.input_tokens for r in self.runs if r.success and r.input_tokens is not None]
        return round(statistics.mean(vals), 0) if vals else None

    @property
    def avg_output_tokens(self) -> Optional[float]:
        vals = [r.output_tokens for r in self.runs if r.success and r.output_tokens is not None]
        return round(statistics.mean(vals), 0) if vals else None


def estimate_cost(input_tokens: int, output_tokens: int, input_per_m: float = 0.10, output_per_m: float = 0.40) -> float:
    return (input_tokens * input_per_m + output_tokens * output_per_m) / 1_000_000
