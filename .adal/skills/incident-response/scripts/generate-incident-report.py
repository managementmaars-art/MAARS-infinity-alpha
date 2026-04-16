#!/usr/bin/env python3
"""
generate-incident-report.py -- Generate a structured incident report.

Creates a markdown incident report and a JSON summary from provided
incident details. Used during or after an incident to document findings.

Usage:
    python generate-incident-report.py \
        --title "Database connection pool exhaustion" \
        --severity SEV2 \
        --start-time "2024-01-15T14:30:00Z" \
        --end-time "2024-01-15T15:15:00Z" \
        --output-dir ./post-mortems/

    python generate-incident-report.py \
        --title "API gateway 502 errors" \
        --severity SEV1 \
        --start-time "2024-01-15T14:30:00Z" \
        --impact "All API requests returning 502" \
        --root-cause "Expired TLS certificate on load balancer" \
        --output-dir ./post-mortems/
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a structured incident report"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Incident title (brief description)",
    )
    parser.add_argument(
        "--severity",
        required=True,
        choices=["SEV1", "SEV2", "SEV3", "SEV4"],
        help="Incident severity level",
    )
    parser.add_argument(
        "--start-time",
        required=True,
        help="Incident start time in ISO 8601 format (e.g., 2024-01-15T14:30:00Z)",
    )
    parser.add_argument(
        "--end-time",
        default=None,
        help="Incident end time in ISO 8601 format (omit if ongoing)",
    )
    parser.add_argument(
        "--output-dir",
        default="./incident-reports",
        help="Directory for report output files (default: ./incident-reports)",
    )
    parser.add_argument(
        "--impact",
        default="",
        help="Description of user-facing impact",
    )
    parser.add_argument(
        "--root-cause",
        default="",
        help="Root cause (if known)",
    )
    parser.add_argument(
        "--commander",
        default="",
        help="Incident commander name",
    )
    parser.add_argument(
        "--services-affected",
        nargs="+",
        default=[],
        help="List of affected services",
    )
    parser.add_argument(
        "--timeline-events",
        nargs="+",
        default=[],
        help="Timeline events in 'HH:MM description' format",
    )
    return parser.parse_args()


def parse_iso_time(time_str: str) -> datetime:
    """Parse an ISO 8601 time string."""
    try:
        if time_str.endswith("Z"):
            time_str = time_str[:-1] + "+00:00"
        return datetime.fromisoformat(time_str)
    except ValueError:
        print(f"ERROR: Invalid time format: {time_str}", file=sys.stderr)
        print("Expected ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ", file=sys.stderr)
        sys.exit(1)


def calculate_duration(start: datetime, end: datetime | None) -> str:
    """Calculate human-readable duration between two times."""
    if end is None:
        return "Ongoing"
    delta = end - start
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m {seconds}s"


def generate_markdown_report(args: argparse.Namespace, duration: str) -> str:
    """Generate a markdown incident report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status = "Resolved" if args.end_time else "Ongoing"

    services = ", ".join(args.services_affected) if args.services_affected else "TBD"

    report = f"""# Incident Report: {args.title}

## Summary

| Field | Value |
|-------|-------|
| **Severity** | {args.severity} |
| **Status** | {status} |
| **Start Time** | {args.start_time} |
| **End Time** | {args.end_time or "Ongoing"} |
| **Duration** | {duration} |
| **Commander** | {args.commander or "TBD"} |
| **Services Affected** | {services} |
| **Report Generated** | {now} |

## Impact

{args.impact or "_Describe the user-facing impact here._"}

## Timeline

| Time (UTC) | Event |
|------------|-------|
| {args.start_time} | Incident detected |
"""

    if args.timeline_events:
        for event in args.timeline_events:
            parts = event.split(" ", 1)
            if len(parts) == 2:
                report += f"| {parts[0]} | {parts[1]} |\n"
            else:
                report += f"| -- | {event} |\n"

    if args.end_time:
        report += f"| {args.end_time} | Incident resolved |\n"

    report += f"""
_Add more timeline entries as the investigation progresses._

## Root Cause

{args.root_cause or "_To be determined during post-mortem investigation._"}

## Contributing Factors

- _List conditions that made the incident more likely or more severe_
- _Example: No alert configured for connection pool usage_
- _Example: Recent deployment changed database query pattern_

## Detection

- How was the incident detected? (Alert, user report, monitoring dashboard)
- How long between incident start and detection?
- Could detection have been faster?

## Response

- What mitigation steps were taken?
- Were the right people involved quickly enough?
- Was the runbook helpful?

## What Went Well

- _Example: Alert fired within 2 minutes of impact_
- _Example: Rollback procedure worked correctly_
- _Example: Clear communication in incident channel_

## What Could Be Improved

- _Example: No alert for connection pool exhaustion_
- _Example: Took 10 minutes to identify the root cause_
- _Example: Runbook did not cover this failure mode_

## Action Items

| Action | Owner | Priority | Due Date | Status |
|--------|-------|----------|----------|--------|
| _Add alert for [metric]_ | TBD | High | TBD | Open |
| _Add regression test for [scenario]_ | TBD | Medium | TBD | Open |
| _Update runbook with [procedure]_ | TBD | Medium | TBD | Open |
| _Fix root cause in [component]_ | TBD | High | TBD | Open |

## Lessons Learned

_Key takeaways from this incident that the broader team should know about._

---

_This report was generated by `generate-incident-report.py`. Fill in the TBD
sections during the post-mortem meeting._
"""
    return report


def main() -> int:
    args = parse_args()

    # Setup output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse times
    start_time = parse_iso_time(args.start_time)
    end_time = parse_iso_time(args.end_time) if args.end_time else None
    duration = calculate_duration(start_time, end_time)

    # Generate file names
    date_prefix = start_time.strftime("%Y%m%d")
    safe_title = args.title.lower().replace(" ", "-")[:50]
    base_name = f"incident-{date_prefix}-{safe_title}"

    markdown_file = output_dir / f"{base_name}.md"
    json_file = output_dir / f"{base_name}.json"

    # Generate markdown report
    markdown_content = generate_markdown_report(args, duration)
    with open(markdown_file, "w") as f:
        f.write(markdown_content)

    # Generate JSON summary
    json_summary = {
        "title": args.title,
        "severity": args.severity,
        "status": "resolved" if args.end_time else "ongoing",
        "start_time": args.start_time,
        "end_time": args.end_time,
        "duration": duration,
        "commander": args.commander or None,
        "impact": args.impact or None,
        "root_cause": args.root_cause or None,
        "services_affected": args.services_affected,
        "timeline_events": args.timeline_events,
        "report_generated": datetime.now(timezone.utc).isoformat(),
        "files": {
            "markdown": str(markdown_file),
            "json": str(json_file),
        },
    }

    with open(json_file, "w") as f:
        json.dump(json_summary, f, indent=2, default=str)

    # Output summary
    print(f"Incident report generated:")
    print(f"  Markdown: {markdown_file}")
    print(f"  JSON:     {json_file}")
    print(f"  Severity: {args.severity}")
    print(f"  Duration: {duration}")
    print(f"  Status:   {'Resolved' if args.end_time else 'Ongoing'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
