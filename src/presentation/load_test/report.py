from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.presentation.load_test.metrics import LoadTestMetrics

console = Console()


def _compute_stats(metrics: LoadTestMetrics, wall_elapsed: float):
    sorted_lat = sorted(metrics.latencies)
    return {
        "sorted_lat": sorted_lat,
        "p50": sorted_lat[len(sorted_lat) // 2],
        "p95": sorted_lat[int(len(sorted_lat) * 0.95)],
        "p99": sorted_lat[int(len(sorted_lat) * 0.99)],
        "avg": sum(metrics.latencies) / len(metrics.latencies),
        "min": sorted_lat[0],
        "max": sorted_lat[-1],
        "throughput": metrics.total / wall_elapsed,
    }


def print_report(
    metrics: LoadTestMetrics,
    test_name: str,
    wall_elapsed: float,
    handler: str,
    concurrency: int,
) -> None:
    """Print a Rich-formatted report to the console."""
    if not metrics.latencies:
        console.print("[yellow]No data.[/yellow]")
        return

    s = _compute_stats(metrics, wall_elapsed)

    # --- Overview table ---
    overview = Table(show_header=False, box=None, padding=(0, 2))
    overview.add_column("key", style="dim")
    overview.add_column("value")
    overview.add_row("Handler", f"[bold]{handler}[/bold]")
    overview.add_row("Concurrency", str(concurrency))
    overview.add_row("Wall time", f"{wall_elapsed:.2f}s")
    overview.add_row(
        "Throughput", f"[bold cyan]{s['throughput']:.1f}[/bold cyan] updates/sec"
    )

    # --- Results table ---
    error_rate = metrics.errors / metrics.total * 100
    error_style = "bold red" if metrics.errors > 0 else "green"

    results = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    results.add_column("Metric", style="dim")
    results.add_column("Value", justify="right")
    results.add_row("Total processed", str(metrics.total))
    results.add_row("Success", f"[green]{metrics.success}[/green]")
    results.add_row("Errors", f"[{error_style}]{metrics.errors}[/{error_style}]")
    results.add_row("Error rate", f"[{error_style}]{error_rate:.1f}%[/{error_style}]")

    # --- Latency table ---
    latency = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    latency.add_column("Percentile", style="dim")
    latency.add_column("Latency", justify="right")
    latency.add_row("Avg", f"{s['avg'] * 1000:.1f} ms")
    latency.add_row("p50", f"{s['p50'] * 1000:.1f} ms")
    latency.add_row("p95", f"[yellow]{s['p95'] * 1000:.1f} ms[/yellow]")
    latency.add_row("p99", f"[red]{s['p99'] * 1000:.1f} ms[/red]")
    latency.add_row("Min", f"{s['min'] * 1000:.1f} ms")
    latency.add_row("Max", f"[red]{s['max'] * 1000:.1f} ms[/red]")

    # --- Compose panel ---
    console.print()
    console.print(
        Panel(
            overview,
            title=f"[bold]{test_name}[/bold]",
            subtitle="Configuration",
            border_style="blue",
        )
    )
    console.print(Panel(results, title="Results", border_style="green"))
    console.print(Panel(latency, title="Latency", border_style="cyan"))

    # --- Errors ---
    if metrics.error_types:
        error_table = Table(
            show_header=True, header_style="bold red", box=None, padding=(0, 2)
        )
        error_table.add_column("Error type")
        error_table.add_column("Count", justify="right")
        for err_type, count in metrics.error_types.items():
            error_table.add_row(err_type, str(count))
        console.print(Panel(error_table, title="Error types", border_style="red"))

    if metrics.first_error_tb:
        tb_text = Text(metrics.first_error_tb.strip())
        tb_text.stylize("dim")
        console.print(Panel(tb_text, title="First error traceback", border_style="red"))


def format_report(
    metrics: LoadTestMetrics,
    test_name: str,
    wall_elapsed: float,
    handler: str,
    concurrency: int,
) -> str:
    """Format metrics into a plain-text report string (for file saving)."""
    if not metrics.latencies:
        return "No data."

    s = _compute_stats(metrics, wall_elapsed)
    error_rate = metrics.errors / metrics.total * 100

    lines = [
        "",
        "=" * 60,
        f"  {test_name}",
        "=" * 60,
        f"  Handler:             {handler}",
        f"  Concurrency:         {concurrency}",
        f"  Wall time:           {wall_elapsed:.2f}s",
        f"  Throughput:          {s['throughput']:.1f} updates/sec",
        "",
        f"  Total processed:     {metrics.total}",
        f"  Success:             {metrics.success}",
        f"  Errors:              {metrics.errors}",
        f"  Error rate:          {error_rate:.1f}%",
        "",
        f"  Avg latency:         {s['avg'] * 1000:.1f} ms",
        f"  p50:                 {s['p50'] * 1000:.1f} ms",
        f"  p95:                 {s['p95'] * 1000:.1f} ms",
        f"  p99:                 {s['p99'] * 1000:.1f} ms",
        f"  Min:                 {s['min'] * 1000:.1f} ms",
        f"  Max:                 {s['max'] * 1000:.1f} ms",
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
