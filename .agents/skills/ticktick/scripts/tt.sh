#!/usr/bin/env bash
# tt.sh — TickTick CLI for Changi
# Usage: tt.sh <command> [options]
# Commands: list, tasks, add, complete, delete, update, projects, add-project, delete-project
set -euo pipefail

BASE_URL="https://api.ticktick.com/open/v1"
TOKEN="${TICKTICK_TOKEN:-}"

# ── Auth ───────────────────────────────────────────────────────────────────────
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: TICKTICK_TOKEN not set" >&2
  exit 1
fi

CURL="curl -s -H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json'"

_get()  { curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL$1"; }
_post() { curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$2" "$BASE_URL$1"; }
_del()  { curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE_URL$1"; }

# ── Helpers ────────────────────────────────────────────────────────────────────
usage() {
  cat >&2 <<EOF
Usage: tt.sh <command> [options]

Commands:
  projects                          List all projects
  tasks [--project <name|id>]       List tasks (default: inbox)
  add <title> [options]             Create a task
    --project <name|id>             Target project (default: inbox)
    --priority <none|low|med|high>  Priority
    --due <YYYY-MM-DDTHH:MM:SS>     Due date (ART, -03:00 appended)
    --notes <text>                  Description
    --tag <tag1,tag2>               Tags (comma-separated)
  complete <taskId> --project <id>  Mark task complete
  delete <taskId> --project <id>    Delete task
  update <taskId> --project <id> [--title X] [--priority X] [--due X]
  add-project <name> [--color #hex] Create project
  delete-project <id>               Delete project
EOF
  exit 1
}

priority_val() {
  case "${1,,}" in
    none)  echo 0 ;;
    low)   echo 1 ;;
    med|medium) echo 3 ;;
    high)  echo 5 ;;
    *)     echo "ERROR: Invalid priority '$1'. Use: none, low, med, high" >&2; exit 1 ;;
  esac
}

# Resolve project name → id
resolve_project() {
  local input="$1"
  if [[ "$input" == "inbox" ]]; then
    echo "inbox131039472"; return
  fi
  # If looks like an ID already (hex string), return as-is
  if [[ "$input" =~ ^[0-9a-f]{24}$ ]]; then
    echo "$input"; return
  fi
  # Look up by name
  local id
  id=$(_get "/project" | python3 -c "
import sys, json
projects = json.load(sys.stdin)
name = '$input'.lower()
for p in projects:
    if p['name'].lower() == name:
        print(p['id'])
        exit()
" 2>/dev/null)
  if [[ -z "$id" ]]; then
    echo "ERROR: Project '$input' not found" >&2; exit 1
  fi
  echo "$id"
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

# ── Commands ───────────────────────────────────────────────────────────────────

case "$CMD" in

  projects)
    _get "/project" | python3 -c "
import sys, json
projects = json.load(sys.stdin)
print(f'📁 {len(projects)} projects')
for p in projects:
    print(f'  {p[\"id\"]}  {p[\"name\"]}')
"
    ;;

  tasks)
    PROJECT="inbox"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) PROJECT="$2"; shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    PROJECT_ID=$(resolve_project "$PROJECT")
    _get "/project/$PROJECT_ID/data" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tasks = [t for t in data.get('tasks', []) if t.get('status', 0) == 0]
PRIORITY = {0:'     ', 1:'[LOW] ', 3:'[MED] ', 5:'[HIGH]'}
tasks.sort(key=lambda t: (-t.get('priority',0), t.get('dueDate','')))
print(f'📋 {len(tasks)} pending tasks')
for t in tasks:
    due = ''
    if t.get('dueDate'):
        due = '  — due ' + t['dueDate'][:10]
    p = PRIORITY.get(t.get('priority',0), '     ')
    print(f'  ○ {p} {t[\"title\"]}{due}')
"
    ;;

  add)
    [[ $# -lt 1 ]] && { echo "ERROR: title required" >&2; exit 1; }
    TITLE="$1"; shift
    PROJECT="inbox"; PRIORITY=0; DUE=""; NOTES=""; TAGS=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project)  PROJECT="$2";  shift 2 ;;
        --priority) PRIORITY=$(priority_val "$2"); shift 2 ;;
        --due)      DUE="${2}-03:00"; shift 2 ;;
        --notes)    NOTES="$2";    shift 2 ;;
        --tag)      TAGS="$2";     shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    PROJECT_ID=$(resolve_project "$PROJECT")
    # Build JSON
    BODY=$(python3 -c "
import json, sys
d = {
  'title': sys.argv[1],
  'projectId': sys.argv[2],
  'priority': int(sys.argv[3]),
  'timeZone': 'America/Buenos_Aires'
}
if sys.argv[4]: d['dueDate'] = sys.argv[4]
if sys.argv[5]: d['content'] = sys.argv[5]
if sys.argv[6]: d['tags'] = [t.strip() for t in sys.argv[6].split(',')]
print(json.dumps(d))
" "$TITLE" "$PROJECT_ID" "$PRIORITY" "$DUE" "$NOTES" "$TAGS")
    RESULT=$(_post "/task" "$BODY")
    echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'errorCode' in d:
    print(f'ERROR: {d[\"errorMessage\"]}', file=sys.stderr)
    exit(1)
PRIORITY = {0:'none', 1:'low', 3:'medium', 5:'high'}
due = f'  due {d[\"dueDate\"][:10]}' if d.get('dueDate') else ''
print(f'✅ Created: {d[\"title\"]}{due} [{PRIORITY.get(d.get(\"priority\",0),\"none\")} priority]')
print(f'   id: {d[\"id\"]}')
"
    ;;

  complete)
    [[ $# -lt 1 ]] && { echo "ERROR: taskId required" >&2; exit 1; }
    TASK_ID="$1"; shift
    PROJECT_ID=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) PROJECT_ID=$(resolve_project "$2"); shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    [[ -z "$PROJECT_ID" ]] && PROJECT_ID="inbox131039472"
    _post "/project/$PROJECT_ID/task/$TASK_ID/complete" "{}" > /dev/null
    echo "✅ Task $TASK_ID marked complete"
    ;;

  delete)
    [[ $# -lt 1 ]] && { echo "ERROR: taskId required" >&2; exit 1; }
    TASK_ID="$1"; shift
    PROJECT_ID=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project) PROJECT_ID=$(resolve_project "$2"); shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    [[ -z "$PROJECT_ID" ]] && PROJECT_ID="inbox131039472"
    _del "/project/$PROJECT_ID/task/$TASK_ID" > /dev/null
    echo "🗑️  Task $TASK_ID deleted"
    ;;

  update)
    [[ $# -lt 1 ]] && { echo "ERROR: taskId required" >&2; exit 1; }
    TASK_ID="$1"; shift
    PROJECT_ID="inbox131039472"; TITLE=""; PRIORITY=""; DUE=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --project)  PROJECT_ID=$(resolve_project "$2"); shift 2 ;;
        --title)    TITLE="$2";  shift 2 ;;
        --priority) PRIORITY=$(priority_val "$2"); shift 2 ;;
        --due)      DUE="${2}-03:00"; shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    BODY=$(python3 -c "
import json, sys
d = {'id': sys.argv[1], 'projectId': sys.argv[2]}
if sys.argv[3]: d['title'] = sys.argv[3]
if sys.argv[4] != '': d['priority'] = int(sys.argv[4])
if sys.argv[5]: d['dueDate'] = sys.argv[5]
print(json.dumps(d))
" "$TASK_ID" "$PROJECT_ID" "$TITLE" "$PRIORITY" "$DUE")
    _post "/task/$TASK_ID" "$BODY" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'errorCode' in d:
    print(f'ERROR: {d[\"errorMessage\"]}', file=sys.stderr); exit(1)
print(f'✅ Updated: {d.get(\"title\", \"task\")}')
"
    ;;

  add-project)
    [[ $# -lt 1 ]] && { echo "ERROR: name required" >&2; exit 1; }
    NAME="$1"; shift
    COLOR="#4A90E2"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --color) COLOR="$2"; shift 2 ;;
        *) echo "ERROR: Unknown option $1" >&2; exit 1 ;;
      esac
    done
    BODY=$(python3 -c "import json,sys; print(json.dumps({'name':sys.argv[1],'color':sys.argv[2],'viewMode':'list'}))" "$NAME" "$COLOR")
    _post "/project" "$BODY" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'errorCode' in d:
    print(f'ERROR: {d[\"errorMessage\"]}', file=sys.stderr); exit(1)
print(f'✅ Project created: {d[\"name\"]} (id: {d[\"id\"]})')
"
    ;;

  delete-project)
    [[ $# -lt 1 ]] && { echo "ERROR: projectId required" >&2; exit 1; }
    _del "/project/$1" > /dev/null
    echo "🗑️  Project $1 deleted"
    ;;

  *) usage ;;
esac
