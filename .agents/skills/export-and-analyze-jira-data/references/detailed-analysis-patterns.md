# Detailed Analysis Patterns for Jira Data

This reference provides comprehensive examples for analyzing exported Jira data, including advanced filtering, aggregation, and reporting patterns.

## Advanced Filtering After Export

### Filter with jq

Extract only open issues:
```bash
jq '.issues[] | select(.fields.status.name == "Open")' issues.json > open_issues.json
```

Get issue keys and summaries:
```bash
jq '.issues[] | {key: .key, summary: .fields.summary}' issues.json > keys_summaries.jsonl
```

Count by status:
```bash
jq '.issues | group_by(.fields.status.name) | map({status: .[0].fields.status.name, count: length})' issues.json
```

### Filter with Python

Convert JSON to CSV with selected fields:
```python
import json
import csv

# Convert JSON to CSV (with selected fields)
with open('issues.json') as f:
    data = json.load(f)

with open('issues_simple.csv', 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=['key', 'summary', 'status', 'priority'])
    writer.writeheader()

    for issue in data['issues']:
        writer.writerow({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'priority': issue['fields']['priority']['name'] if issue['fields'].get('priority') else 'N/A'
        })
```

Aggregate by status:
```python
import json
from collections import defaultdict

with open('issues.json') as f:
    data = json.load(f)

# Count by status
by_status = defaultdict(int)
for issue in data['issues']:
    status = issue['fields']['status']['name']
    by_status[status] += 1

print("Issues by Status:")
for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
    print(f"  {status}: {count}")
```

## Analysis Patterns

### Analysis 1: Status Distribution

```python
import json
from collections import Counter

with open('issues.json') as f:
    data = json.load(f)

statuses = Counter(
    issue['fields']['status']['name']
    for issue in data['issues']
)

print("Status Distribution:")
for status, count in statuses.most_common():
    pct = (count / len(data['issues'])) * 100
    print(f"  {status}: {count} ({pct:.1f}%)")
```

### Analysis 2: Workload by Assignee

```python
import json
from collections import Counter

with open('issues.json') as f:
    data = json.load(f)

assignees = Counter()
for issue in data['issues']:
    assignee = issue['fields']['assignee']
    if assignee:
        assignees[assignee['displayName']] += 1

print("Workload Distribution:")
for name, count in assignees.most_common(10):
    print(f"  {name}: {count}")
```

### Analysis 3: Age of Open Issues

```python
import json
from datetime import datetime, UTC

with open('issues.json') as f:
    data = json.load(f)

now = datetime.now(UTC)
open_issues = [
    issue for issue in data['issues']
    if issue['fields']['status']['name'] != 'Done'
]

# Calculate age
for issue in open_issues[:5]:  # Top 5
    created = datetime.fromisoformat(
        issue['fields']['created'].replace('Z', '+00:00')
    )
    age = (now - created).days
    print(f"{issue['key']}: {age} days old")
```

### Analysis 4: Priority vs Status Correlation

```python
import json

with open('issues.json') as f:
    data = json.load(f)

matrix = {}
for issue in data['issues']:
    priority = issue['fields']['priority']['name'] if issue['fields'].get('priority') else 'None'
    status = issue['fields']['status']['name']

    key = (priority, status)
    matrix[key] = matrix.get(key, 0) + 1

print("Priority vs Status Matrix:")
print("Priority\tTo Do\tIn Progress\tDone")
for priority in ['Highest', 'High', 'Medium', 'Low']:
    row = f"{priority}"
    for status in ['To Do', 'In Progress', 'Done']:
        count = matrix.get((priority, status), 0)
        row += f"\t{count}"
    print(row)
```

## Export for External Tools

### Export for BI Tools (Tableau, Power BI)

```bash
# CSV format for most BI tools
uv run jira-tool export --all --format csv -o issues_for_bi.csv

# Or combine with advanced tools
# Power BI: CSV import with automatic refresh
# Tableau: Direct CSV or API connection
```

### Export for Analytics (Spreadsheet)

```bash
# Export to CSV, then open in Excel/Google Sheets
uv run jira-tool export --format csv -o team_metrics.csv

# In spreadsheet: Add formulas, pivot tables, charts
```

### Export for Reporting (Markdown/HTML)

```python
import json
import csv

# Read JSON, write Markdown report
with open('issues.json') as f:
    data = json.load(f)

with open('report.md', 'w') as out:
    out.write("# Jira Export Report\n\n")
    out.write(f"Total Issues: {len(data['issues'])}\n\n")
    out.write("## Issues\n\n")
    out.write("| Key | Summary | Status |\n")
    out.write("|-----|---------|--------|\n")

    for issue in data['issues'][:20]:  # First 20
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        out.write(f"| {key} | {summary} | {status} |\n")
```

### Export for Archive (JSON Backup)

```bash
# Keep full JSON backup with all data
uv run jira-tool export --all \
  --expand "changelog,transitions" \
  --format json \
  -o archive_$(date +%Y%m%d).json
```

## Complete Examples

### Example 1: Weekly Metrics Report

```bash
#!/bin/bash
# Export this week's activity
uv run jira-tool export \
  --project PROJ \
  --created "-7d" \
  --format json \
  -o weekly_issues.json

# Analyze
python3 << 'EOF'
import json
from datetime import datetime, UTC, timedelta

with open('weekly_issues.json') as f:
    data = json.load(f)

issues = data['issues']
now = datetime.now(UTC)
week_ago = now - timedelta(days=7)

print(f"Weekly Metrics ({week_ago.date()} to {now.date()})")
print(f"====================================")
print(f"Total Issues Created: {len(issues)}")

by_status = {}
for issue in issues:
    status = issue['fields']['status']['name']
    by_status[status] = by_status.get(status, 0) + 1

print("\nBy Status:")
for status, count in sorted(by_status.items()):
    print(f"  {status}: {count}")
EOF
```

### Example 2: Archive Old Issues with History

```bash
# Export all closed issues with full changelog (for archive)
uv run jira-tool search "status = Done AND updated <= -30d" \
  --expand changelog \
  --format jsonl \
  -o archived_issues.jsonl

# Verify integrity
wc -l archived_issues.jsonl
```

### Example 3: Prepare Data for Analysis Tool

```bash
# Export with all expansions for external analysis
uv run jira-tool search "sprint in openSprints()" \
  --expand "changelog,transitions,operations" \
  --format json \
  -o sprint_full.json

# Convert to simplified CSV for Excel analysis
python3 << 'EOF'
import json
import csv

with open('sprint_full.json') as f:
    data = json.load(f)

with open('sprint_analysis.csv', 'w', newline='') as out:
    fields = ['key', 'summary', 'status', 'assignee', 'created', 'updated']
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()

    for issue in data['issues']:
        assignee = issue['fields']['assignee']
        writer.writerow({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'assignee': assignee['displayName'] if assignee else 'Unassigned',
            'created': issue['fields']['created'],
            'updated': issue['fields']['updated']
        })

print(f"Converted {len(data['issues'])} issues to CSV")
EOF
```

### Example 4: Compare Two Projects

```bash
# Export both projects
uv run jira-tool export --project PROJ1 --format jsonl -o proj1.jsonl
uv run jira-tool export --project PROJ2 --format jsonl -o proj2.jsonl

# Analyze differences
python3 << 'EOF'
import json
from collections import Counter

def analyze_file(filename):
    statuses = Counter()
    types = Counter()
    count = 0
    for line in open(filename):
        issue = json.loads(line)
        statuses[issue['fields']['status']['name']] += 1
        types[issue['fields']['issuetype']['name']] += 1
        count += 1
    return count, statuses, types

proj1_count, proj1_status, proj1_types = analyze_file('proj1.jsonl')
proj2_count, proj2_status, proj2_types = analyze_file('proj2.jsonl')

print(f"PROJ1: {proj1_count} issues")
print(f"  Status: {dict(proj1_status)}")
print(f"PROJ2: {proj2_count} issues")
print(f"  Status: {dict(proj2_status)}")
EOF
```

## Processing JSONL Efficiently

When working with large JSONL files:

Count issues:
```bash
wc -l issues.jsonl
```

Filter with jq:
```bash
jq 'select(.fields.status.name == "In Progress")' issues.jsonl > in_progress.jsonl
```

Extract specific field:
```bash
jq '.key' issues.jsonl | wc -l
```

Python streaming:
```python
import json

total = 0
for line in open('issues.jsonl'):
    issue = json.loads(line)
    if issue['fields']['status']['name'] == 'In Progress':
        total += 1

print(f"In Progress: {total}")
```
