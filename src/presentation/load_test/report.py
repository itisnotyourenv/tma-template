from datetime import datetime
from pathlib import Path

from src.presentation.load_test.metrics import LoadTestMetrics


def format_report(
    metrics: LoadTestMetrics,
    test_name: str,
    wall_elapsed: float,
    handler: str,
    concurrency: int,
) -> str:
    """Format metrics into a human-readable report string."""
    if not metrics.latencies:
        return "No data."

    sorted_lat = sorted(metrics.latencies)
    p50 = sorted_lat[len(sorted_lat) // 2]
    p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
    p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
    avg = sum(metrics.latencies) / len(metrics.latencies)
    throughput = metrics.total / wall_elapsed

    lines = [
        "",
        "=" * 60,
        f"  {test_name}",
        "=" * 60,
        f"  Handler:             {handler}",
        f"  Concurrency:         {concurrency}",
        f"  Wall time:           {wall_elapsed:.2f}s",
        f"  Throughput:          {throughput:.1f} updates/sec",
        "",
        f"  Total processed:     {metrics.total}",
        f"  Success:             {metrics.success}",
        f"  Errors:              {metrics.errors}",
        f"  Error rate:          {metrics.errors / metrics.total * 100:.1f}%",
        "",
        f"  Avg latency:         {avg * 1000:.1f} ms",
        f"  p50:                 {p50 * 1000:.1f} ms",
        f"  p95:                 {p95 * 1000:.1f} ms",
        f"  p99:                 {p99 * 1000:.1f} ms",
        f"  Min:                 {sorted_lat[0] * 1000:.1f} ms",
        f"  Max:                 {sorted_lat[-1] * 1000:.1f} ms",
        "",
    ]

    if metrics.error_types:
        lines.append("  Error types:")
        for err_type, count in metrics.error_types.items():
            lines.append(f"    {err_type}: {count}")

    if metrics.first_error_tb:
        lines.append("")
        lines.append("  First error (full traceback):")
        lines.append("  " + "-" * 40)
        for line in metrics.first_error_tb.strip().splitlines():
            lines.append(f"  {line}")
        lines.append("  " + "-" * 40)

    lines.append("=" * 60)
    return "\n".join(lines)


def save_report(report_text: str, test_name: str) -> Path:
    """Save report to reports/ directory. Returns the file path."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = test_name.replace(" ", "_").replace("/", "-")
    filename = f"{timestamp}_{safe_name}.txt"
    filepath = reports_dir / filename

    filepath.write_text(report_text, encoding="utf-8")
    return filepath
