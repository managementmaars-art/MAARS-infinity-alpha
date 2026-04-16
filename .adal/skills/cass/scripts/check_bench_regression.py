#!/usr/bin/env python3
"""
check_bench_regression.py

Compares Criterion benchmark results to detect performance regressions.
Used in CI to fail builds that exceed the configured threshold.

Features:
- Metric-specific thresholds (latency, duration, memory, throughput)
- Historical trend tracking across multiple runs
- Trend analysis to detect sustained regressions vs noise
- JSON and human-readable output

Usage:
    python scripts/check_bench_regression.py --threshold 10
    python scripts/check_bench_regression.py --threshold 5 --baseline main --current pr
    python scripts/check_bench_regression.py --save-history --history-file perf_history.json
    python scripts/check_bench_regression.py --analyze-trends --history-file perf_history.json

Metric-specific thresholds (T5.3 spec):
    - Duration (test suite): 20% regression threshold
    - Latency (search P50/P95): 10% regression threshold
    - Memory (peak RSS): 15% regression threshold
    - Throughput (indexing): 10% regression threshold
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Metric type classification patterns and their thresholds
METRIC_PATTERNS = {
    "latency": {
        "patterns": ["search", "query", "latency", "p50", "p95", "lookup"],
        "threshold": 10.0,
        "description": "Search/query latency metrics",
    },
    "duration": {
        "patterns": ["duration", "time", "suite", "total", "full", "batch"],
        "threshold": 20.0,
        "description": "Test/task duration metrics",
    },
    "memory": {
        "patterns": ["memory", "mem", "rss", "heap", "alloc", "peak"],
        "threshold": 15.0,
        "description": "Memory usage metrics",
    },
    "throughput": {
        "patterns": ["throughput", "index", "ingest", "rate", "per_sec", "convs"],
        "threshold": 10.0,
        "description": "Throughput/indexing metrics",
    },
}

# Default threshold for unclassified metrics
DEFAULT_THRESHOLD = 10.0


def classify_metric(name: str) -> tuple[str, float]:
    """Classify a metric by name and return (type, threshold)."""
    name_lower = name.lower()
    for metric_type, config in METRIC_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern in name_lower:
                return metric_type, config["threshold"]
    return "other", DEFAULT_THRESHOLD


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check for benchmark regressions with metric-specific thresholds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Metric thresholds (configurable):
  --latency-threshold   Search/query latency (default: 10%)
  --duration-threshold  Test/task duration (default: 20%)
  --memory-threshold    Memory usage (default: 15%)
  --throughput-threshold Indexing throughput (default: 10%)
""",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override all thresholds with a single value",
    )
    # Per-metric thresholds
    parser.add_argument(
        "--latency-threshold",
        type=float,
        default=METRIC_PATTERNS["latency"]["threshold"],
        help=f"Latency regression threshold (default: {METRIC_PATTERNS['latency']['threshold']}%%)",
    )
    parser.add_argument(
        "--duration-threshold",
        type=float,
        default=METRIC_PATTERNS["duration"]["threshold"],
        help=f"Duration regression threshold (default: {METRIC_PATTERNS['duration']['threshold']}%%)",
    )
    parser.add_argument(
        "--memory-threshold",
        type=float,
        default=METRIC_PATTERNS["memory"]["threshold"],
        help=f"Memory regression threshold (default: {METRIC_PATTERNS['memory']['threshold']}%%)",
    )
    parser.add_argument(
        "--throughput-threshold",
        type=float,
        default=METRIC_PATTERNS["throughput"]["threshold"],
        help=f"Throughput regression threshold (default: {METRIC_PATTERNS['throughput']['threshold']}%%)",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default="main",
        help="Baseline benchmark name (default: main)",
    )
    parser.add_argument(
        "--current",
        type=str,
        default="pr",
        help="Current benchmark name (default: pr)",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default="target",
        help="Cargo target directory (default: target)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error on any regression (regardless of threshold)",
    )
    # Historical tracking
    parser.add_argument(
        "--history-file",
        type=str,
        default=None,
        help="Path to JSON file for storing benchmark history",
    )
    parser.add_argument(
        "--save-history",
        action="store_true",
        help="Save current results to history file",
    )
    parser.add_argument(
        "--analyze-trends",
        action="store_true",
        help="Analyze historical trends for sustained regressions",
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=30,
        help="Maximum number of historical entries to keep (default: 30)",
    )
    parser.add_argument(
        "--trend-window",
        type=int,
        default=5,
        help="Number of recent runs to analyze for trends (default: 5)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Unique identifier for this run (e.g., commit SHA, PR number)",
    )
    return parser.parse_args()


def get_thresholds(args: argparse.Namespace) -> dict[str, float]:
    """Get the threshold map based on arguments."""
    if args.threshold is not None:
        # Single threshold overrides all
        return {
            "latency": args.threshold,
            "duration": args.threshold,
            "memory": args.threshold,
            "throughput": args.threshold,
            "other": args.threshold,
        }
    return {
        "latency": args.latency_threshold,
        "duration": args.duration_threshold,
        "memory": args.memory_threshold,
        "throughput": args.throughput_threshold,
        "other": DEFAULT_THRESHOLD,
    }


def find_criterion_dir(target_dir: str) -> Optional[Path]:
    """Find the criterion benchmark directory."""
    criterion_path = Path(target_dir) / "criterion"
    if criterion_path.exists():
        return criterion_path
    return None


def load_benchmark_estimates(criterion_dir: Path, bench_name: str) -> dict:
    """Load benchmark estimates from criterion JSON files."""
    estimates = {}

    for bench_group in criterion_dir.iterdir():
        if not bench_group.is_dir():
            continue

        for bench in bench_group.iterdir():
            if not bench.is_dir():
                continue

            estimates_file = bench / bench_name / "estimates.json"
            if estimates_file.exists():
                try:
                    with open(estimates_file) as f:
                        data = json.load(f)
                        # Criterion stores estimates with "mean" containing "point_estimate"
                        if "mean" in data and "point_estimate" in data["mean"]:
                            key = f"{bench_group.name}/{bench.name}"
                            estimates[key] = data["mean"]["point_estimate"]
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Could not parse {estimates_file}: {e}", file=sys.stderr)

    return estimates


def compare_benchmarks(
    baseline: dict,
    current: dict,
    thresholds: dict[str, float],
) -> tuple[list, list, list]:
    """Compare benchmark results using metric-specific thresholds."""
    regressions = []
    improvements = []
    unchanged = []

    for name, current_time in current.items():
        if name not in baseline:
            continue

        baseline_time = baseline[name]
        if baseline_time == 0:
            continue

        diff_pct = ((current_time - baseline_time) / baseline_time) * 100

        # Get metric-specific threshold
        metric_type, _ = classify_metric(name)
        threshold = thresholds.get(metric_type, DEFAULT_THRESHOLD)

        result = {
            "name": name,
            "baseline_ns": baseline_time,
            "current_ns": current_time,
            "diff_pct": diff_pct,
            "metric_type": metric_type,
            "threshold": threshold,
        }

        if diff_pct > threshold:
            regressions.append(result)
        elif diff_pct < -threshold:
            improvements.append(result)
        else:
            unchanged.append(result)

    return regressions, improvements, unchanged


# --- Historical Tracking ---


def load_history(history_file: str) -> dict:
    """Load benchmark history from JSON file."""
    path = Path(history_file)
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load history: {e}", file=sys.stderr)
    return {"version": 1, "runs": []}


def save_history(history: dict, history_file: str, limit: int = 30):
    """Save benchmark history to JSON file, keeping only the last N entries."""
    # Trim to limit
    if len(history["runs"]) > limit:
        history["runs"] = history["runs"][-limit:]

    path = Path(history_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def add_to_history(
    history: dict,
    current: dict,
    run_id: Optional[str] = None,
) -> dict:
    """Add current benchmark results to history."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "benchmarks": current,
    }
    history["runs"].append(entry)
    return history


def analyze_trends(history: dict, window: int = 5) -> dict:
    """Analyze trends across recent benchmark runs.

    Returns trend analysis including:
    - Sustained regressions (multiple runs showing regression)
    - Improving metrics (consistent improvement over time)
    - Volatile metrics (high variance)
    """
    runs = history.get("runs", [])
    if len(runs) < 2:
        return {"status": "insufficient_data", "runs_available": len(runs)}

    # Get the last N runs
    recent_runs = runs[-window:] if len(runs) >= window else runs

    # Collect all benchmark names
    all_benchmarks = set()
    for run in recent_runs:
        all_benchmarks.update(run.get("benchmarks", {}).keys())

    trends = {
        "sustained_regressions": [],
        "improving": [],
        "volatile": [],
        "stable": [],
        "window_size": len(recent_runs),
    }

    for bench_name in all_benchmarks:
        values = []
        for run in recent_runs:
            if bench_name in run.get("benchmarks", {}):
                values.append(run["benchmarks"][bench_name])

        if len(values) < 2:
            continue

        # Calculate statistics
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            continue

        # Check for sustained regression (each run slower than previous)
        regression_count = sum(
            1 for i in range(1, len(values)) if values[i] > values[i - 1] * 1.05
        )
        improvement_count = sum(
            1 for i in range(1, len(values)) if values[i] < values[i - 1] * 0.95
        )

        # Calculate coefficient of variation (volatility)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        std_dev = variance**0.5
        cv = (std_dev / mean_val) * 100 if mean_val > 0 else 0

        # Overall change from first to last
        total_change_pct = ((values[-1] - values[0]) / values[0]) * 100 if values[0] > 0 else 0

        metric_type, threshold = classify_metric(bench_name)
        trend_data = {
            "name": bench_name,
            "metric_type": metric_type,
            "values": values,
            "mean_ns": mean_val,
            "std_dev_ns": std_dev,
            "cv_pct": cv,
            "total_change_pct": total_change_pct,
            "regression_count": regression_count,
            "improvement_count": improvement_count,
        }

        # Categorize
        if cv > 20:
            trends["volatile"].append(trend_data)
        elif regression_count >= len(values) - 1 and total_change_pct > threshold:
            trends["sustained_regressions"].append(trend_data)
        elif improvement_count >= len(values) - 1 and total_change_pct < -threshold:
            trends["improving"].append(trend_data)
        else:
            trends["stable"].append(trend_data)

    return trends


def format_ns(ns: float) -> str:
    """Format nanoseconds to human-readable string."""
    if ns >= 1_000_000_000:
        return f"{ns / 1_000_000_000:.2f}s"
    elif ns >= 1_000_000:
        return f"{ns / 1_000_000:.2f}ms"
    elif ns >= 1_000:
        return f"{ns / 1_000:.2f}μs"
    else:
        return f"{ns:.0f}ns"


def print_results(
    regressions: list,
    improvements: list,
    unchanged: list,
    thresholds: dict[str, float],
):
    """Print benchmark comparison results with metric-specific thresholds."""
    print("\n" + "=" * 60)
    print("BENCHMARK REGRESSION CHECK")
    print("=" * 60 + "\n")

    # Group regressions by metric type
    if regressions:
        print("⚠️  REGRESSIONS:")
        print("-" * 40)

        # Group by metric type for better organization
        by_type: dict[str, list] = {}
        for r in regressions:
            mt = r.get("metric_type", "other")
            by_type.setdefault(mt, []).append(r)

        for metric_type, items in sorted(by_type.items()):
            threshold = thresholds.get(metric_type, DEFAULT_THRESHOLD)
            print(f"\n  [{metric_type.upper()}] (threshold: {threshold}%)")
            for r in sorted(items, key=lambda x: x["diff_pct"], reverse=True):
                print(f"    {r['name']}")
                print(f"      Baseline: {format_ns(r['baseline_ns'])}")
                print(f"      Current:  {format_ns(r['current_ns'])}")
                print(f"      Change:   +{r['diff_pct']:.1f}% (>{r['threshold']}%)")
        print()

    if improvements:
        print("✅ IMPROVEMENTS:")
        print("-" * 40)

        by_type: dict[str, list] = {}
        for i in improvements:
            mt = i.get("metric_type", "other")
            by_type.setdefault(mt, []).append(i)

        for metric_type, items in sorted(by_type.items()):
            threshold = thresholds.get(metric_type, DEFAULT_THRESHOLD)
            print(f"\n  [{metric_type.upper()}] (threshold: {threshold}%)")
            for i in sorted(items, key=lambda x: x["diff_pct"]):
                print(f"    {i['name']}")
                print(f"      Baseline: {format_ns(i['baseline_ns'])}")
                print(f"      Current:  {format_ns(i['current_ns'])}")
                print(f"      Change:   {i['diff_pct']:.1f}%")
        print()

    print("📊 SUMMARY:")
    print("-" * 40)
    print(f"  Regressions:  {len(regressions)}")
    print(f"  Improvements: {len(improvements)}")
    print(f"  Unchanged:    {len(unchanged)}")
    print()
    print("  Thresholds by metric type:")
    for mt, thresh in sorted(thresholds.items()):
        print(f"    {mt}: ±{thresh}%")
    print()


def print_trends(trends: dict):
    """Print trend analysis results."""
    print("\n" + "=" * 60)
    print("TREND ANALYSIS")
    print("=" * 60 + "\n")

    if trends.get("status") == "insufficient_data":
        print(f"⚠️  Insufficient data for trend analysis (runs: {trends.get('runs_available', 0)})")
        print("   Need at least 2 historical runs.")
        return

    print(f"Analyzed last {trends['window_size']} runs\n")

    if trends["sustained_regressions"]:
        print("🔴 SUSTAINED REGRESSIONS (action required):")
        print("-" * 40)
        for t in sorted(trends["sustained_regressions"], key=lambda x: x["total_change_pct"], reverse=True):
            print(f"  {t['name']} [{t['metric_type']}]")
            print(f"    Total change: +{t['total_change_pct']:.1f}%")
            print(f"    Mean: {format_ns(t['mean_ns'])}, StdDev: {format_ns(t['std_dev_ns'])}")
        print()

    if trends["improving"]:
        print("🟢 CONSISTENTLY IMPROVING:")
        print("-" * 40)
        for t in sorted(trends["improving"], key=lambda x: x["total_change_pct"]):
            print(f"  {t['name']} [{t['metric_type']}]")
            print(f"    Total change: {t['total_change_pct']:.1f}%")
        print()

    if trends["volatile"]:
        print("🟡 VOLATILE (high variance):")
        print("-" * 40)
        for t in sorted(trends["volatile"], key=lambda x: x["cv_pct"], reverse=True):
            print(f"  {t['name']} [{t['metric_type']}]")
            print(f"    CV: {t['cv_pct']:.1f}% (may indicate flaky measurement)")
        print()

    print(f"📊 Stable metrics: {len(trends['stable'])}")
    print()


def main():
    args = parse_args()
    thresholds = get_thresholds(args)

    # Handle trend analysis mode (doesn't need criterion data)
    if args.analyze_trends:
        if not args.history_file:
            print("Error: --history-file required for trend analysis", file=sys.stderr)
            sys.exit(2)

        history = load_history(args.history_file)
        trends = analyze_trends(history, args.trend_window)

        if args.json:
            print(json.dumps(trends, indent=2))
        else:
            print_trends(trends)

        # Exit with error if sustained regressions found
        if trends.get("sustained_regressions"):
            print(
                f"❌ FAIL: {len(trends['sustained_regressions'])} sustained regression(s) detected",
                file=sys.stderr,
            )
            sys.exit(1)

        print("✅ PASS: No sustained regressions in trend analysis")
        sys.exit(0)

    # Standard benchmark comparison mode
    criterion_dir = find_criterion_dir(args.target_dir)
    if not criterion_dir:
        print("Warning: No criterion benchmark data found.", file=sys.stderr)
        print("Run benchmarks first: cargo bench --bench <name> -- --save-baseline main", file=sys.stderr)
        # Exit successfully if no benchmark data exists (first run)
        sys.exit(0)

    baseline = load_benchmark_estimates(criterion_dir, args.baseline)
    current = load_benchmark_estimates(criterion_dir, args.current)

    if not baseline:
        print(f"Warning: No baseline '{args.baseline}' benchmark data found.", file=sys.stderr)
        sys.exit(0)

    if not current:
        print(f"Warning: No current '{args.current}' benchmark data found.", file=sys.stderr)
        sys.exit(0)

    # Save to history if requested
    if args.save_history and args.history_file:
        history = load_history(args.history_file)
        history = add_to_history(history, current, args.run_id)
        save_history(history, args.history_file, args.history_limit)
        print(f"Saved benchmark results to {args.history_file}", file=sys.stderr)

    regressions, improvements, unchanged = compare_benchmarks(
        baseline, current, thresholds
    )

    if args.json:
        output = {
            "thresholds": thresholds,
            "regressions": regressions,
            "improvements": improvements,
            "unchanged_count": len(unchanged),
            "has_regressions": len(regressions) > 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": args.run_id,
        }
        print(json.dumps(output, indent=2))
    else:
        print_results(regressions, improvements, unchanged, thresholds)

    # Exit with error if regressions exceed threshold
    if regressions:
        if args.strict:
            print("❌ FAIL: Regressions detected (--strict mode)", file=sys.stderr)
            sys.exit(1)
        else:
            # Group regressions by type for summary
            by_type: dict[str, int] = {}
            for r in regressions:
                mt = r.get("metric_type", "other")
                by_type[mt] = by_type.get(mt, 0) + 1

            summary = ", ".join(f"{count} {mt}" for mt, count in sorted(by_type.items()))
            print(f"❌ FAIL: {len(regressions)} regression(s): {summary}", file=sys.stderr)
            sys.exit(1)

    print("✅ PASS: No significant regressions detected")
    sys.exit(0)


if __name__ == "__main__":
    main()
