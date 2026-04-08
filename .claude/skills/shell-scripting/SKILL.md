---
name: shell-scripting
description: Bash scripting, sed/awk, process substitution, here docs, cron, error handling, CI/CD scripts
---

# Shell Scripting

Production-grade Bash scripting: robust error handling, sed/awk text processing, process substitution, heredocs, cron scheduling, and CI/CD automation scripts.

## Script Skeleton with Best Practices

Every production script starts with strict mode, usage documentation, and cleanup:

```bash
#!/usr/bin/env bash
# deploy.sh — Deploy application to target environment
# Usage: ./deploy.sh [-e ENV] [-v VERSION] [-d] [--dry-run]
# Options:
#   -e ENV      Target environment (dev|staging|prod) [default: dev]
#   -v VERSION  Version tag to deploy [default: latest]
#   -d          Enable debug output
#   --dry-run   Print actions without executing

set -euo pipefail          # exit on error, unset vars, pipe failures
IFS=$'\n\t'               # safer word splitting

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'      # No Color

# Globals
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/deploy-$(date +%Y%m%d-%H%M%S).log"
ENV="dev"
VERSION="latest"
DRY_RUN=false
DEBUG=false

# Logging
log()   { echo -e "[$(date +'%T')] $*" | tee -a "$LOG_FILE"; }
info()  { log "${GREEN}[INFO]${NC}  $*"; }
warn()  { log "${YELLOW}[WARN]${NC}  $*" >&2; }
error() { log "${RED}[ERROR]${NC} $*" >&2; }
debug() { [[ "$DEBUG" == true ]] && log "[DEBUG] $*" || true; }
die()   { error "$*"; exit 1; }

# Cleanup on exit
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        error "Script failed with exit code $exit_code"
        error "Check log: $LOG_FILE"
    fi
}
trap cleanup EXIT
trap 'die "Caught SIGINT"' INT
trap 'die "Caught SIGTERM"' TERM

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e) ENV="$2"; shift 2 ;;
            -v) VERSION="$2"; shift 2 ;;
            -d) DEBUG=true; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            -h|--help) usage; exit 0 ;;
            *) die "Unknown option: $1" ;;
        esac
    done
    validate_args
}

validate_args() {
    [[ "$ENV" =~ ^(dev|staging|prod)$ ]] || die "Invalid env: $ENV. Must be dev|staging|prod"
    [[ -n "$VERSION" ]] || die "Version cannot be empty"
}

usage() {
    sed -n '2,6p' "$0" | sed 's/^# //'
}

# Run or dry-run a command
run() {
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY-RUN] $*"
    else
        debug "Running: $*"
        "$@"
    fi
}

main() {
    mkdir -p "$(dirname "$LOG_FILE")"
    parse_args "$@"
    info "Deploying version=$VERSION to env=$ENV"
    # ... deployment steps
}

main "$@"
```

## sed and awk for Text Processing

```bash
# --- sed examples ---

# Replace first occurrence per line
sed 's/old/new/' file.txt

# Replace all occurrences (-g flag in awk; sed uses /g)
sed 's/old/new/g' file.txt

# In-place edit with backup
sed -i.bak 's/APP_VERSION=.*/APP_VERSION=2.1.0/' .env

# Delete lines matching pattern
sed '/^#/d; /^$/d' config.txt          # remove comments and blank lines

# Print lines 10-20
sed -n '10,20p' large_file.txt

# Multi-line: append after match
sed '/\[section\]/a\new_key=value' config.ini

# Extract value from key=value
VERSION=$(sed -n 's/^version = //p' pyproject.toml)

# --- awk examples ---

# Sum a column
awk '{sum += $3} END {print sum}' data.csv

# Filter and transform
awk -F',' '$4 > 1000 {printf "%-20s %s\n", $1, $4}' sales.csv

# Multi-file join by key
awk -F',' 'FNR==NR {a[$1]=$2; next} $1 in a {print $0, a[$1]}' users.csv orders.csv

# Parse log timestamps and compute duration
awk '/START/{start=$2} /END/{split($2,t,":"); end=t[1]*3600+t[2]*60+t[3]; \
    split(start,s,":"); s=s[1]*3600+s[2]*60+s[3]; print "Duration:", end-s, "sec"}' app.log

# AWK as a report generator
awk -F',' '
BEGIN { print "=== Sales Report ===" }
NR > 1 {
    region[$2] += $4
    count[$2]++
}
END {
    for (r in region) {
        printf "%-15s total=%d avg=%.2f\n", r, region[r], region[r]/count[r]
    }
}' sales.csv | sort
```

## Process Substitution and Pipelines

```bash
# Process substitution: treat command output as a file
diff <(ssh host1 cat /etc/hosts) <(ssh host2 cat /etc/hosts)

# Join two sorted streams without temp files
join <(sort -k1 users.txt) <(sort -k1 orders.txt)

# Read while loop that doesn't fork a subshell (bash 4+)
while IFS=',' read -r id name email; do
    echo "Processing user: $name ($email)"
done < <(psql -c "SELECT id,name,email FROM users" -t -A -F',')

# Parallel processing with process substitution
process_chunk() {
    local chunk_file=$1
    while IFS= read -r line; do
        process_line "$line"
    done < "$chunk_file"
}

# Split input into N chunks and process in parallel
split -l 1000 big_file.txt chunk_
for f in chunk_*; do
    process_chunk "$f" &
done
wait   # wait for all background jobs
rm chunk_*

# Named pipes for streaming
mkfifo /tmp/mypipe
producer > /tmp/mypipe &
consumer < /tmp/mypipe
```

## Here Documents and Strings

```bash
# Basic heredoc
cat <<'EOF' > /etc/nginx/sites-available/app
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Heredoc with variable expansion (no quotes on delimiter)
DB_NAME="myapp_prod"
psql postgres <<EOF
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO appuser;
EOF

# Indented heredoc (<<-)
if [[ "$ENV" == "prod" ]]; then
    cat <<-EOF
        Deploying to production!
        Version: $VERSION
        Time: $(date)
    EOF
fi

# Herestring: feed a string to stdin
wc -w <<< "Hello World from herestring"
read first rest <<< "one two three four"
echo "First: $first, Rest: $rest"
```

## Cron Job Patterns

```bash
# /etc/cron.d/myapp — system cron with environment
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=ops@example.com

# Every day at 2 AM UTC — database backup
0 2 * * *   deploy /opt/app/scripts/backup.sh >> /var/log/backup.log 2>&1

# Every 5 minutes — health check
*/5 * * * * deploy /opt/app/scripts/healthcheck.sh || /opt/app/scripts/alert.sh

# First day of month at midnight
0 0 1 * *   root /opt/app/scripts/monthly_report.sh

# Weekdays at 9 AM
0 9 * * 1-5 deploy /opt/app/scripts/morning_report.sh

# Robust cron wrapper script
cat <<'CRON_WRAPPER' > /opt/app/scripts/cron_wrapper.sh
#!/usr/bin/env bash
set -euo pipefail
LOCK_FILE="/tmp/$(basename "$0").lock"
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "Already running"; exit 0; }
export $(grep -v '^#' /opt/app/.env | xargs)
exec "$@"
CRON_WRAPPER
```

## CI/CD Automation Scripts

```bash
#!/usr/bin/env bash
# ci-build.sh — CI/CD build pipeline
set -euo pipefail

VERSION="${CI_COMMIT_TAG:-$(git describe --tags --always --dirty)}"
IMAGE="registry.example.com/myapp:${VERSION}"
CACHE_IMAGE="registry.example.com/myapp:cache"

# Retry function for flaky network operations
retry() {
    local max=$1; shift
    local delay=$1; shift
    local attempt=0
    until "$@"; do
        attempt=$((attempt + 1))
        if [[ $attempt -ge $max ]]; then
            echo "Command failed after $max attempts: $*" >&2
            return 1
        fi
        echo "Attempt $attempt failed. Retrying in ${delay}s..."
        sleep "$delay"
    done
}

# Build with BuildKit and cache
build_image() {
    DOCKER_BUILDKIT=1 docker build \
        --cache-from "$CACHE_IMAGE" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --build-arg VERSION="$VERSION" \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        -t "$IMAGE" \
        -t "$CACHE_IMAGE" \
        .
}

# Run tests in parallel
run_tests() {
    local -a pids=()
    pytest tests/unit/ -n auto &           pids+=($!)
    pytest tests/integration/ -m "not slow" & pids+=($!)
    npm run test:unit &                    pids+=($!)

    local failed=0
    for pid in "${pids[@]}"; do
        wait "$pid" || failed=$((failed + 1))
    done
    return $failed
}

# Semantic version bump
bump_version() {
    local type="${1:-patch}"    # major|minor|patch
    local current
    current=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    IFS='.' read -r major minor patch <<< "${current#v}"
    case "$type" in
        major) major=$((major+1)); minor=0; patch=0 ;;
        minor) minor=$((minor+1)); patch=0 ;;
        patch) patch=$((patch+1)) ;;
    esac
    echo "v${major}.${minor}.${patch}"
}

# Check required tools
check_dependencies() {
    local deps=("docker" "git" "jq" "kubectl" "helm")
    local missing=()
    for dep in "${deps[@]}"; do
        command -v "$dep" &>/dev/null || missing+=("$dep")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing dependencies: ${missing[*]}" >&2
        return 1
    fi
}

check_dependencies
retry 3 5 build_image
run_tests
retry 3 5 docker push "$IMAGE"
retry 3 5 docker push "$CACHE_IMAGE"
echo "Build complete: $IMAGE"
```

## Best Practices

- Always use `set -euo pipefail` and `IFS=$'\n\t'` at the top of every script
- Use `[[ ]]` instead of `[ ]` for conditional tests (supports regex, no word splitting)
- Quote all variable expansions: `"$var"`, `"${array[@]}"` — unquoted variables are a common bug source
- Use `local` for all variables inside functions to avoid polluting global scope
- Prefer `mapfile -t lines < file` over `while read` loops for reading files into arrays
- Use `mktemp` for temp files and clean them up with `trap cleanup EXIT`
- Use `flock` to prevent concurrent cron job execution
- Avoid parsing `ls` output — use globs: `for f in /path/*.log; do`
- Use `printf` instead of `echo` for reliable output formatting
- Test scripts with `shellcheck` before committing — catches most common pitfalls

## Models to Use

- **Default**: `claude-sonnet-4-5` — complex scripts, pipelines, error handling
- **Architecture**: `claude-opus-4-5` — large multi-script systems, CI/CD pipeline design
- **Quick snippets**: `claude-haiku-3-5` — one-liners, simple transformations, cron expressions
