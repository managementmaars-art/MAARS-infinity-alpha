# Scenario NN: Input Ingestion

**Time:** ~15m
**Environment:** staging | local | both
**Parallel Safe:** Yes
**Requires:** None

Verifies that the app correctly accepts, processes, and stores uploaded/imported files. Covers happy path ingestion, cross-format support, metadata extraction, and error handling for rejected inputs.

## Prerequisites

- Scenario 00-smoke passes
- Project deployed with ingestion service running
- Required secrets set (storage credentials, processing API keys)

## Fixtures

| File | Type | Size | Purpose | Provenance |
|------|------|------|---------|------------|
| `fixtures/sample-document.md` | Markdown | ~2 KB | Happy path — minimal valid | Hand-written |
| `fixtures/sample-report.pdf` | PDF | ~15 KB | Cross-format coverage | Generated via `scripts/make-fixtures.sh` |
| `fixtures/sample-import.csv` | CSV | ~1 KB | Structured data import | Hand-written, 50 rows |
| `fixtures/empty-file.md` | Markdown | 0 B | Boundary — empty file | `touch` |
| `fixtures/wrong-type.txt` | Text | ~100 B | Boundary — wrong MIME | Hand-written |

See `fixtures/README.md` for full provenance details.

### Fixture Validation

```bash
# Verify all fixtures exist before starting
FIXTURES=(
  "fixtures/sample-document.md"
  "fixtures/sample-report.pdf"
  "fixtures/sample-import.csv"
  "fixtures/empty-file.md"
  "fixtures/wrong-type.txt"
)

MISSING=0
for f in "${FIXTURES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    MISSING=1
  fi
done

if [[ $MISSING -eq 1 ]]; then
  echo "Run: scripts/make-fixtures.sh to generate missing fixtures"
  exit 1
fi

echo "All fixtures present"
```

## Setup

```bash
# Environment detection
if [[ "$EVE_API_URL" == https://* ]]; then
  ENV_TYPE="cloud"
  APP_SCHEME="https"
  APP_DOMAIN="${EVE_API_URL#https://api.}"
else
  ENV_TYPE="local"
  APP_SCHEME="http"
  APP_DOMAIN="lvh.me"
fi

# Auth
eve auth login --email "${EVE_EMAIL}" --ssh-key "${EVE_SSH_KEY}"
TOKEN=$(eve auth token --raw)

# Project variables
ORG_SLUG="your-org"
PROJECT_SLUG="your-project"
ENV_NAME="staging"

# App API base URL — CUSTOMIZE
APP_API="${APP_SCHEME}://api.${ORG_SLUG}-${PROJECT_SLUG}-${ENV_NAME}.${APP_DOMAIN}"
```

## Phases

### Phase 1: Happy Path — Markdown Upload

```bash
# Upload the Markdown fixture
UPLOAD_RESULT=$(curl -sf -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/sample-document.md" \
  "${APP_API}/ingest" | jq '.')

DOC_ID=$(echo "$UPLOAD_RESULT" | jq -r '.id')
echo "Uploaded: $DOC_ID"

# Verify the document was stored
DOC=$(curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_API}/documents/${DOC_ID}" | jq '.')

echo "$DOC" | jq '{id, name, mime_type, status, size}'
```

**Expected:**
- Upload returns 201 with a document ID
- Document retrievable via GET
- MIME type is `text/markdown`
- Status is `processed` or `pending` (depending on async processing)
- File size matches fixture size

### Phase 2: Cross-Format — PDF Upload

```bash
# Upload the PDF fixture
PDF_RESULT=$(curl -sf -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/sample-report.pdf" \
  "${APP_API}/ingest" | jq '.')

PDF_ID=$(echo "$PDF_RESULT" | jq -r '.id')

# Verify
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_API}/documents/${PDF_ID}" | jq '{id, mime_type, status}'
```

**Expected:**
- Upload returns 201
- MIME type is `application/pdf`
- Document is processed (text extracted, if applicable)

### Phase 3: Structured Data — CSV Import

```bash
# Import the CSV fixture
CSV_RESULT=$(curl -sf -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/sample-import.csv" \
  "${APP_API}/import" | jq '.')

IMPORT_ID=$(echo "$CSV_RESULT" | jq -r '.id')

# Verify row count
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_API}/imports/${IMPORT_ID}" | jq '{id, rows_imported, status}'
```

**Expected:**
- Import returns 201 with an import ID
- Row count matches fixture (50 rows)
- Status is `completed`
- No rows skipped or errored

### Phase 4: Boundary — Empty File

```bash
# Upload empty file
EMPTY_RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/empty-file.md" \
  -w "\n%{http_code}" \
  "${APP_API}/ingest")

HTTP_CODE=$(echo "$EMPTY_RESULT" | tail -1)
BODY=$(echo "$EMPTY_RESULT" | head -1)

echo "Status: $HTTP_CODE"
echo "Body: $BODY"
```

**Expected:**
- Returns 400 or 422 (not 500)
- Error message explains rejection reason (e.g., "file is empty")
- No partial record created in the database

### Phase 5: Boundary — Wrong MIME Type

```bash
# Upload wrong type (plain text renamed as something else)
WRONG_RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/wrong-type.txt;type=application/pdf" \
  -w "\n%{http_code}" \
  "${APP_API}/ingest")

HTTP_CODE=$(echo "$WRONG_RESULT" | tail -1)
echo "Status: $HTTP_CODE"
```

**Expected:**
- Returns 400 or 422 (not 500)
- Error message indicates MIME mismatch or unsupported type
- No corrupt record created

### Phase 6: Downstream Processing Verification

```bash
# Check that the successfully uploaded document was processed
# Wait for async processing if needed
sleep 5

# Verify processing result — CUSTOMIZE for your app
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_API}/documents/${DOC_ID}" | jq '{status, processed_at, word_count, chunks}'
```

**Expected:**
- Document status is `processed` (not `pending` or `failed`)
- Processing metadata is populated (word count, chunks, etc.)
- Processing completed within expected time window

## Success Criteria

### Phase 1 — Markdown Upload
- [ ] Upload returns 201 with document ID
- [ ] Document retrievable via GET
- [ ] MIME type is `text/markdown`
- [ ] File size matches fixture

### Phase 2 — PDF Upload
- [ ] Upload returns 201
- [ ] MIME type is `application/pdf`
- [ ] Document processed successfully

### Phase 3 — CSV Import
- [ ] Import returns 201 with import ID
- [ ] Row count matches fixture (50 rows)
- [ ] Status is `completed`

### Phase 4 — Empty File
- [ ] Returns 400/422, not 500
- [ ] Error message explains rejection
- [ ] No partial record created

### Phase 5 — Wrong MIME
- [ ] Returns 400/422, not 500
- [ ] Error indicates type mismatch

### Phase 6 — Processing
- [ ] Document status is `processed`
- [ ] Metadata populated correctly

## Debugging

| Symptom | Diagnostic | Fix |
|---------|-----------|-----|
| Upload returns 413 | Check ingress body-size annotation | Add `proxy-body-size: "50m"` in manifest |
| Upload returns 500 | Check service logs: `eve job logs` or `kubectl logs` | Fix server-side validation |
| Processing stuck at `pending` | Check worker/queue health | Restart processing worker |
| MIME detection wrong | Check `Content-Type` header in request | Ensure correct MIME in `curl -F` |
| CSV import skips rows | Check import error details | Fix CSV format or parser config |
| Empty file creates record | Check validation middleware | Add size > 0 check before persistence |

## Cleanup

```bash
# Remove uploaded test documents
for id in $DOC_ID $PDF_ID; do
  curl -sf -X DELETE -H "Authorization: Bearer $TOKEN" \
    "${APP_API}/documents/${id}" && echo "Deleted: $id"
done

# Remove import
curl -sf -X DELETE -H "Authorization: Bearer $TOKEN" \
  "${APP_API}/imports/${IMPORT_ID}" && echo "Deleted import: $IMPORT_ID"

echo "Cleanup complete"
```
