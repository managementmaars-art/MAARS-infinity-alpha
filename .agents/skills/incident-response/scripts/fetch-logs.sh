#!/usr/bin/env bash
#
# fetch-logs.sh -- Fetch recent logs from application services
#
# Retrieves logs from Docker containers for the specified service
# and time range. Writes raw logs and a filtered error summary to
# the output directory.
#
# Usage:
#   ./fetch-logs.sh --service backend --since "15 minutes ago" --output-dir ./logs/
#   ./fetch-logs.sh --service db --since "1 hour ago" --output-dir ./logs/ --filter ERROR
#
set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────────
SERVICE=""
SINCE="15m"
OUTPUT_DIR="./incident-logs"
FILTER=""
CONTAINER_PREFIX="app"
TAIL_LINES=1000

# ─── Parse Arguments ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --service)          SERVICE="$2"; shift 2 ;;
    --since)            SINCE="$2"; shift 2 ;;
    --output-dir)       OUTPUT_DIR="$2"; shift 2 ;;
    --filter)           FILTER="$2"; shift 2 ;;
    --container-prefix) CONTAINER_PREFIX="$2"; shift 2 ;;
    --tail)             TAIL_LINES="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --service <service-name> --output-dir <dir>"
      echo ""
      echo "Options:"
      echo "  --service          Service name (backend, frontend, db, redis)"
      echo "  --since            Time range for logs (default: 15m)"
      echo "  --output-dir       Directory for log output files"
      echo "  --filter           Filter logs by pattern (e.g., ERROR, WARNING)"
      echo "  --container-prefix Container name prefix (default: app)"
      echo "  --tail             Maximum number of lines (default: 1000)"
      exit 0
      ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$SERVICE" ]]; then
  echo "ERROR: --service is required" >&2
  exit 1
fi

# ─── Setup Output ────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RAW_LOG_FILE="${OUTPUT_DIR}/${SERVICE}-raw-${TIMESTAMP}.log"
ERROR_LOG_FILE="${OUTPUT_DIR}/${SERVICE}-errors-${TIMESTAMP}.log"
SUMMARY_FILE="${OUTPUT_DIR}/${SERVICE}-summary-${TIMESTAMP}.json"

log() {
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $1"
}

# ─── Determine Container Name ────────────────────────────────────────────────
CONTAINER_NAME="${CONTAINER_PREFIX}-${SERVICE}"

# Verify container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  log "ERROR: Container '${CONTAINER_NAME}' not found"
  log "Available containers:"
  docker ps -a --format '{{.Names}}' | while read -r name; do
    log "  - ${name}"
  done

  cat > "$SUMMARY_FILE" <<EOJSON
{
  "service": "${SERVICE}",
  "container": "${CONTAINER_NAME}",
  "status": "error",
  "error": "Container not found",
  "timestamp": "${TIMESTAMP}"
}
EOJSON
  exit 1
fi

# ─── Fetch Logs ──────────────────────────────────────────────────────────────
log "Fetching logs from ${CONTAINER_NAME} (since ${SINCE})..."

# Fetch raw logs
docker logs "${CONTAINER_NAME}" --since "${SINCE}" --tail "${TAIL_LINES}" \
  > "$RAW_LOG_FILE" 2>&1

TOTAL_LINES=$(wc -l < "$RAW_LOG_FILE")
log "Fetched ${TOTAL_LINES} lines of logs"

# ─── Extract Errors ─────────────────────────────────────────────────────────
log "Extracting errors and warnings..."

grep -iE "(ERROR|CRITICAL|FATAL|Exception|Traceback)" "$RAW_LOG_FILE" \
  > "$ERROR_LOG_FILE" 2>/dev/null || true

ERROR_LINES=$(wc -l < "$ERROR_LOG_FILE")
log "Found ${ERROR_LINES} error/exception lines"

# ─── Apply Custom Filter ────────────────────────────────────────────────────
FILTER_LINES=0
FILTER_FILE=""
if [[ -n "$FILTER" ]]; then
  FILTER_FILE="${OUTPUT_DIR}/${SERVICE}-filtered-${TIMESTAMP}.log"
  grep -i "$FILTER" "$RAW_LOG_FILE" > "$FILTER_FILE" 2>/dev/null || true
  FILTER_LINES=$(wc -l < "$FILTER_FILE")
  log "Filter '${FILTER}' matched ${FILTER_LINES} lines"
fi

# ─── Error Pattern Analysis ─────────────────────────────────────────────────
log "Analyzing error patterns..."

# Count error types
ERROR_COUNTS=""
if [[ $ERROR_LINES -gt 0 ]]; then
  ERROR_COUNTS=$(grep -oP '(ERROR|CRITICAL|FATAL|\w+Error|\w+Exception)' "$ERROR_LOG_FILE" \
    | sort | uniq -c | sort -rn | head -10 \
    | while read -r count pattern; do
        echo "    {\"pattern\": \"${pattern}\", \"count\": ${count}}"
      done | paste -sd ',' -)
fi

# ─── Container Status ───────────────────────────────────────────────────────
CONTAINER_STATUS=$(docker inspect "${CONTAINER_NAME}" --format '{{.State.Status}}' 2>/dev/null || echo "unknown")
CONTAINER_RESTARTS=$(docker inspect "${CONTAINER_NAME}" --format '{{.RestartCount}}' 2>/dev/null || echo "0")
CONTAINER_STARTED=$(docker inspect "${CONTAINER_NAME}" --format '{{.State.StartedAt}}' 2>/dev/null || echo "unknown")

# ─── Write Summary ──────────────────────────────────────────────────────────
cat > "$SUMMARY_FILE" <<EOJSON
{
  "service": "${SERVICE}",
  "container": "${CONTAINER_NAME}",
  "timestamp": "${TIMESTAMP}",
  "since": "${SINCE}",
  "status": "collected",
  "container_status": "${CONTAINER_STATUS}",
  "container_restarts": ${CONTAINER_RESTARTS},
  "container_started_at": "${CONTAINER_STARTED}",
  "total_log_lines": ${TOTAL_LINES},
  "error_lines": ${ERROR_LINES},
  "filter_pattern": "${FILTER}",
  "filter_matches": ${FILTER_LINES},
  "files": {
    "raw_log": "${RAW_LOG_FILE}",
    "error_log": "${ERROR_LOG_FILE}",
    "filtered_log": "${FILTER_FILE:-null}",
    "summary": "${SUMMARY_FILE}"
  },
  "top_error_patterns": [${ERROR_COUNTS}]
}
EOJSON

# ─── Output Summary ─────────────────────────────────────────────────────────
log ""
log "=== Log Collection Summary ==="
log "Service:          ${SERVICE}"
log "Container:        ${CONTAINER_NAME} (${CONTAINER_STATUS})"
log "Restarts:         ${CONTAINER_RESTARTS}"
log "Total lines:      ${TOTAL_LINES}"
log "Error lines:      ${ERROR_LINES}"
if [[ -n "$FILTER" ]]; then
  log "Filter matches:   ${FILTER_LINES} (pattern: ${FILTER})"
fi
log "Raw log:          ${RAW_LOG_FILE}"
log "Error log:        ${ERROR_LOG_FILE}"
log "Summary:          ${SUMMARY_FILE}"

if [[ $ERROR_LINES -gt 0 ]]; then
  log ""
  log "=== Recent Errors (last 5) ==="
  tail -5 "$ERROR_LOG_FILE"
fi

exit 0
