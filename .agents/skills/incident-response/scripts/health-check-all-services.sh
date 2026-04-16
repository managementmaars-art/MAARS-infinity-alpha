#!/usr/bin/env bash
#
# health-check-all-services.sh -- Check health of all application services
#
# Checks liveness and connectivity of backend, frontend, database, and Redis
# services. Writes a structured report to the output directory.
#
# Usage:
#   ./health-check-all-services.sh --output-dir ./health-results/
#   ./health-check-all-services.sh --backend-url https://api.example.com --output-dir ./results/
#
set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────────
OUTPUT_DIR="./health-check-results"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
DB_CONTAINER="${DB_CONTAINER:-app-db}"
REDIS_CONTAINER="${REDIS_CONTAINER:-app-redis}"
TIMEOUT=10

# ─── Parse Arguments ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)      OUTPUT_DIR="$2"; shift 2 ;;
    --backend-url)     BACKEND_URL="$2"; shift 2 ;;
    --frontend-url)    FRONTEND_URL="$2"; shift 2 ;;
    --db-container)    DB_CONTAINER="$2"; shift 2 ;;
    --redis-container) REDIS_CONTAINER="$2"; shift 2 ;;
    --timeout)         TIMEOUT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --output-dir <dir>"
      echo ""
      echo "Options:"
      echo "  --output-dir      Directory for health check result files"
      echo "  --backend-url     Backend service URL (default: http://localhost:8000)"
      echo "  --frontend-url    Frontend service URL (default: http://localhost:3000)"
      echo "  --db-container    Database container name (default: app-db)"
      echo "  --redis-container Redis container name (default: app-redis)"
      echo "  --timeout         HTTP request timeout in seconds (default: 10)"
      exit 0
      ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ─── Setup Output ────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RESULT_FILE="${OUTPUT_DIR}/health-all-services-${TIMESTAMP}.json"
LOG_FILE="${OUTPUT_DIR}/health-all-services-${TIMESTAMP}.log"

log() {
  local msg="[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $1"
  echo "$msg" | tee -a "$LOG_FILE"
}

TOTAL=0
HEALTHY=0
UNHEALTHY=0
RESULTS=""

# ─── Check Function ─────────────────────────────────────────────────────────
check_http() {
  local name="$1"
  local url="$2"
  local expected_status="${3:-200}"

  TOTAL=$((TOTAL + 1))
  log "Checking ${name}: ${url}"

  local start_time
  start_time=$(date +%s%N)

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time "$TIMEOUT" "$url" 2>/dev/null) || http_code="000"

  local end_time
  end_time=$(date +%s%N)
  local elapsed_ms=$(( (end_time - start_time) / 1000000 ))

  local status="unhealthy"
  if [[ "$http_code" == "$expected_status" ]]; then
    status="healthy"
    HEALTHY=$((HEALTHY + 1))
    log "  OK: ${name} returned ${http_code} in ${elapsed_ms}ms"
  else
    UNHEALTHY=$((UNHEALTHY + 1))
    log "  FAIL: ${name} returned ${http_code} (expected ${expected_status}) in ${elapsed_ms}ms"
  fi

  local entry="{\"name\":\"${name}\",\"url\":\"${url}\",\"status\":\"${status}\",\"http_code\":${http_code},\"response_time_ms\":${elapsed_ms}}"
  if [[ -n "$RESULTS" ]]; then
    RESULTS="${RESULTS},${entry}"
  else
    RESULTS="${entry}"
  fi
}

check_container() {
  local name="$1"
  local container="$2"
  local check_cmd="$3"

  TOTAL=$((TOTAL + 1))
  log "Checking ${name}: container ${container}"

  local status="unhealthy"
  local detail=""

  # Check if container is running
  if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
    detail="Container not running"
    UNHEALTHY=$((UNHEALTHY + 1))
    log "  FAIL: ${name} - container '${container}' not running"
  else
    # Run the health check command
    if output=$(docker exec "$container" sh -c "$check_cmd" 2>&1); then
      status="healthy"
      detail="$output"
      HEALTHY=$((HEALTHY + 1))
      log "  OK: ${name} is responsive"
    else
      detail="$output"
      UNHEALTHY=$((UNHEALTHY + 1))
      log "  FAIL: ${name} - ${output}"
    fi
  fi

  local detail_escaped
  detail_escaped=$(echo "$detail" | tr '"' "'" | tr '\n' ' ' | head -c 200)

  local entry="{\"name\":\"${name}\",\"container\":\"${container}\",\"status\":\"${status}\",\"detail\":\"${detail_escaped}\"}"
  if [[ -n "$RESULTS" ]]; then
    RESULTS="${RESULTS},${entry}"
  else
    RESULTS="${entry}"
  fi
}

# ─── Run Health Checks ──────────────────────────────────────────────────────
log "=== Health Check: All Services ==="
log "Timestamp: ${TIMESTAMP}"
log ""

# Backend health checks
log "--- Backend ---"
check_http "Backend Liveness" "${BACKEND_URL}/health" "200"
check_http "Backend Readiness" "${BACKEND_URL}/health/ready" "200"
check_http "Backend API" "${BACKEND_URL}/api/v1/" "200"
log ""

# Frontend health checks
log "--- Frontend ---"
check_http "Frontend" "${FRONTEND_URL}/" "200"
log ""

# Database health checks
log "--- Database ---"
check_container "PostgreSQL" "${DB_CONTAINER}" "pg_isready -U postgres"
log ""

# Redis health checks
log "--- Redis ---"
check_container "Redis" "${REDIS_CONTAINER}" "redis-cli ping"
log ""

# ─── Docker Container Status ────────────────────────────────────────────────
log "--- Container Status ---"
CONTAINER_STATUS=$(docker ps --format "{{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not available")
log "$CONTAINER_STATUS"
log ""

# ─── Write Results ──────────────────────────────────────────────────────────
OVERALL="healthy"
if [[ $UNHEALTHY -gt 0 ]]; then
  OVERALL="unhealthy"
fi

cat > "$RESULT_FILE" <<EOJSON
{
  "timestamp": "${TIMESTAMP}",
  "overall_status": "${OVERALL}",
  "total_checks": ${TOTAL},
  "healthy": ${HEALTHY},
  "unhealthy": ${UNHEALTHY},
  "services": {
    "backend_url": "${BACKEND_URL}",
    "frontend_url": "${FRONTEND_URL}",
    "db_container": "${DB_CONTAINER}",
    "redis_container": "${REDIS_CONTAINER}"
  },
  "results": [${RESULTS}]
}
EOJSON

# ─── Summary ─────────────────────────────────────────────────────────────────
log "=== Health Check Summary ==="
log "Overall: ${OVERALL}"
log "Total: ${TOTAL}  Healthy: ${HEALTHY}  Unhealthy: ${UNHEALTHY}"
log "Results: ${RESULT_FILE}"
log "Log: ${LOG_FILE}"

if [[ $UNHEALTHY -gt 0 ]]; then
  log ""
  log "WARNING: ${UNHEALTHY} service(s) are unhealthy"
  exit 1
fi

log "ALL SERVICES HEALTHY"
exit 0
