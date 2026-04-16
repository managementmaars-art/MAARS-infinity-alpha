# Example: ADR Creation Workflow

## Scenario

User asks: "Document decision to use PostgreSQL"

## Workflow Steps

### 1. Create ADR

```bash
python /path/to/scripts/create_adr.py \
  --title "Use PostgreSQL for Primary Database" \
  --status proposed \
  --context "Need relational database with JSONB support for flexible schema and complex queries"
```

### 2. Add Decision Details

Edit the created ADR README.md to add:
- Detailed context about requirements
- Decision rationale
- Alternatives considered (MySQL, MongoDB)
- Comparison criteria

### 3. Document Consequences

Add to Consequences section:
- **Positive:** Strong ACID guarantees, excellent JSONB support, mature ecosystem
- **Negative:** More complex setup than SQLite, requires maintenance

### 4. Change Status

Once team approves:
- Update status from "proposed" to "accepted"
- Move ADR folder from `docs/adr/in_progress/` to `docs/adr/accepted/`

### 5. Reference in Code

Add references in relevant code files:
```python
# Database configuration
# See: docs/adr/accepted/001-use-postgresql/README.md
DATABASE_URL = "postgresql://..."
```

## Expected Output

**File:** `docs/adr/accepted/001-use-postgresql/README.md`

**Structure:**
- ADR number and title
- Status (accepted)
- Date
- Context section (detailed)
- Decision section (clear)
- Consequences (positive and negative)
- Alternatives considered
- References
