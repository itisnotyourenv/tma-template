import traceback
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class LoadTestMetrics:
    total: int = 0
    success: int = 0
    errors: int = 0
    latencies: list[float] = field(default_factory=list)
    error_types: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    first_error: Exception | None = None
    first_error_tb: str | None = None

    def record_success(self, latency: float) -> None:
        self.total += 1
        self.success += 1
        self.latencies.append(latency)

    def record_error(self, error: Exception, latency: float) -> None:
        self.total += 1
        self.errors += 1
        self.latencies.append(latency)
        self.error_types[f"{type(error).__name__}: {error!s:.80}"] += 1
        if self.first_error is None:
            self.first_error = error
            self.first_error_tb = traceback.format_exc()
