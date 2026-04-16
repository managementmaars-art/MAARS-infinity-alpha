#!/usr/bin/env bash
# bench-report.sh - Run performance benchmarks and generate reports
#
# Usage:
#   ./scripts/bench-report.sh           # Run all benchmarks
#   ./scripts/bench-report.sh --quick   # Run only runtime_perf (fastest)
#   ./scripts/bench-report.sh --save    # Save baseline for comparison
#   ./scripts/bench-report.sh --compare # Compare against saved baseline
#   ./scripts/bench-report.sh --open    # Open HTML report after generation
#
# Benchmarks:
#   - runtime_perf: Search, indexing, wildcard, concurrent, scaling
#   - search_perf:  Vector search, empty query
#   - index_perf:   Full index rebuild
#   - cache_micro:  Cache behavior, typing patterns

set -euo pipefail

QUICK_MODE=false
SAVE_BASELINE=false
COMPARE_BASELINE=false
OPEN_REPORT=false
BASELINE_NAME="main"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            ;;
        --save)
            SAVE_BASELINE=true
            ;;
        --save=*)
            SAVE_BASELINE=true
            BASELINE_NAME="${arg#*=}"
            ;;
        --compare)
            COMPARE_BASELINE=true
            ;;
        --compare=*)
            COMPARE_BASELINE=true
            BASELINE_NAME="${arg#*=}"
            ;;
        --open)
            OPEN_REPORT=true
            ;;
        --help|-h)
            echo "Usage: $0 [--quick] [--save[=name]] [--compare[=name]] [--open]"
            echo ""
            echo "Options:"
            echo "  --quick        Run only runtime_perf benchmark (fastest)"
            echo "  --save[=name]  Save results as baseline (default: main)"
            echo "  --compare[=name] Compare against baseline (default: main)"
            echo "  --open         Open HTML report in browser"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all benchmarks"
            echo "  $0 --quick            # Quick benchmark run"
            echo "  $0 --save=v1.0        # Save baseline named 'v1.0'"
            echo "  $0 --compare=v1.0     # Compare against 'v1.0' baseline"
            echo ""
            exit 0
            ;;
    esac
done

echo "==================================="
echo "  cass Performance Benchmarks"
echo "==================================="
echo ""

# Build in release mode first
echo "Building release binary..."
cargo build --release --quiet

# Determine which benchmarks to run
if [ "$QUICK_MODE" = true ]; then
    BENCH_TARGETS="--bench runtime_perf"
    echo "Running: runtime_perf (quick mode)"
else
    BENCH_TARGETS="--bench runtime_perf --bench search_perf --bench index_perf --bench cache_micro"
    echo "Running: runtime_perf, search_perf, index_perf, cache_micro"
fi
echo ""

# Build benchmark args
BENCH_ARGS=""
if [ "$SAVE_BASELINE" = true ]; then
    BENCH_ARGS="-- --save-baseline $BASELINE_NAME"
    echo "Saving results as baseline: $BASELINE_NAME"
elif [ "$COMPARE_BASELINE" = true ]; then
    BENCH_ARGS="-- --baseline $BASELINE_NAME"
    echo "Comparing against baseline: $BASELINE_NAME"
fi

# Run benchmarks
echo ""
echo "Running benchmarks..."
echo "-----------------------------------"

# shellcheck disable=SC2086
cargo bench $BENCH_TARGETS $BENCH_ARGS 2>&1 | tee /tmp/bench-output.txt

echo ""
echo "-----------------------------------"
echo "Benchmark Summary"
echo "-----------------------------------"

# Extract key metrics from output
if grep -q "time:" /tmp/bench-output.txt; then
    echo ""
    echo "Key Results:"
    grep -E "^(test |    time:|    thrpt:|    change:)" /tmp/bench-output.txt | head -30
fi

# Show report location
echo ""
echo "-----------------------------------"
echo "Reports generated in: target/criterion/"
echo ""
echo "Key reports:"
echo "  - target/criterion/report/index.html (summary)"
echo "  - target/criterion/*/report/index.html (per-benchmark)"

# Open report if requested
if [ "$OPEN_REPORT" = true ]; then
    REPORT_PATH="target/criterion/report/index.html"
    if [ -f "$REPORT_PATH" ]; then
        echo ""
        echo "Opening report in browser..."
        if command -v open &> /dev/null; then
            open "$REPORT_PATH"  # macOS
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$REPORT_PATH"  # Linux
        else
            echo "Could not detect browser opener. Open manually: $REPORT_PATH"
        fi
    fi
fi

echo ""
echo "Done!"
