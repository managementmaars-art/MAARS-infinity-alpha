**Skill**: [ClickHouse Architect](../SKILL.md)

# Cache Schema Evolution

<!-- ADR: 2025-12-09-clickhouse-architect-skill -->

Patterns for managing schema changes in ClickHouse caches without manual invalidation. Covers version columns, content-based validation, and migration strategies.

## Why Schema Evolution Matters

Caching computed results accelerates queries but introduces a hidden cost: **stale data after schema changes**.

| Problem                        | Impact                                        | Example                                    |
| ------------------------------ | --------------------------------------------- | ------------------------------------------ |
| New columns missing from cache | Results lack new features                     | Microstructure columns return NULL         |
| Column semantics changed       | Wrong data served to consumers                | `efficiency` renamed to `density`          |
| Algorithm updated              | Cached results computed with old logic        | Range bar threshold calculation changed    |
| Silent failures                | No errors, just incorrect downstream analysis | ML model trained on incomplete feature set |

**Real-world case**: rangebar-py v7.0 added 10 microstructure columns. Cached data from v6.x returned NULL for `ofi`, `kyle_lambda_proxy`, etc., breaking ML pipelines silently.

## Pattern 1: Schema Version Column

**Cosmos DB-style**: Store a version identifier with each cached record, filter at read time.

### Implementation

```sql
CREATE TABLE cache.range_bars (
    -- Primary data
    symbol LowCardinality(String),
    timestamp_ms Int64,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,

    -- Version column for evolution
    schema_version UInt16 DEFAULT 1,

    -- Or use application version string
    app_version String DEFAULT '',

    -- Computed timestamp for ReplacingMergeTree
    computed_at DateTime64(3) DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(computed_at)
ORDER BY (symbol, timestamp_ms);
```

### Read with Version Filter

```python
import clickhouse_connect

CURRENT_SCHEMA_VERSION = 3  # Increment on breaking changes

def get_cached_bars(client, symbol: str, start_ms: int, end_ms: int):
    """Fetch bars, filtering stale versions."""
    return client.query_df(f"""
        SELECT * FROM cache.range_bars FINAL
        WHERE symbol = %(symbol)s
          AND timestamp_ms BETWEEN %(start)s AND %(end)s
          AND schema_version >= %(version)s
        ORDER BY timestamp_ms
    """, parameters={
        'symbol': symbol,
        'start': start_ms,
        'end': end_ms,
        'version': CURRENT_SCHEMA_VERSION,
    })
```

### When to Increment Version

| Change Type                     | Increment? | Example                             |
| ------------------------------- | ---------- | ----------------------------------- |
| New column added                | Yes        | Added `kyle_lambda_proxy`           |
| Column renamed                  | Yes        | `efficiency` -> `density`           |
| Algorithm changed               | Yes        | Threshold calculation fix           |
| Bug fix affecting output        | Yes        | VWAP computation corrected          |
| Default value changed           | Maybe      | Depends on consumer sensitivity     |
| New optional column (NULL-safe) | No         | Added `description` with DEFAULT '' |

## Pattern 2: ReplacingMergeTree + Version

**Automatic invalidation**: ClickHouse keeps the newest version during merge.

### Implementation

```sql
CREATE TABLE cache.range_bars (
    symbol LowCardinality(String),
    timestamp_ms Int64,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,

    -- Microstructure features (added v7.0)
    ofi Float64 DEFAULT 0,
    vwap_close_deviation Float64 DEFAULT 0,
    kyle_lambda_proxy Float64 DEFAULT 0,

    -- Version for ReplacingMergeTree dedup
    record_version UInt64 DEFAULT 1,
    computed_at DateTime64(3) DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(record_version)
ORDER BY (symbol, timestamp_ms);
```

### Write with Incremented Version

```python
def store_bars(client, df, schema_version: int = 1):
    """Store bars with explicit version for replacement."""
    df = df.copy()
    df['record_version'] = schema_version
    df['computed_at'] = pd.Timestamp.now()
    client.insert_df('cache.range_bars', df)
```

### Query with FINAL

```sql
-- Force deduplication at query time
SELECT * FROM cache.range_bars FINAL
WHERE symbol = 'BTCUSDT'
  AND timestamp_ms BETWEEN 1704067200000 AND 1706745600000
ORDER BY timestamp_ms;
```

**Caveat**: FINAL is slow on large tables (100x overhead). Use partition-aware optimization:

```sql
SET do_not_merge_across_partitions_select_final = 1;
SELECT * FROM cache.range_bars FINAL WHERE ...;
```

## Pattern 3: Content-Based Validation

**Schema-agnostic**: Validate cached data meets current requirements at read time.

### Implementation

```python
from typing import NamedTuple

# Single source of truth for required columns
REQUIRED_COLUMNS = frozenset({
    'timestamp_ms', 'open', 'high', 'low', 'close', 'volume',
})

MICROSTRUCTURE_COLUMNS = frozenset({
    'ofi', 'vwap_close_deviation', 'kyle_lambda_proxy',
    'trade_intensity', 'volume_per_trade', 'aggression_ratio',
})

class CacheValidation(NamedTuple):
    valid: bool
    missing_columns: set[str]
    reason: str

def validate_cached_df(df, include_microstructure: bool = False) -> CacheValidation:
    """Validate cached DataFrame has required columns."""
    required = REQUIRED_COLUMNS.copy()
    if include_microstructure:
        required |= MICROSTRUCTURE_COLUMNS

    present = set(df.columns)
    missing = required - present

    if missing:
        return CacheValidation(
            valid=False,
            missing_columns=missing,
            reason=f"Missing columns: {missing}",
        )

    # Check for NULL values in required columns
    null_cols = [c for c in required if df[c].isnull().any()]
    if null_cols:
        return CacheValidation(
            valid=False,
            missing_columns=set(null_cols),
            reason=f"NULL values in: {null_cols}",
        )

    return CacheValidation(valid=True, missing_columns=set(), reason="")
```

### Usage with Fallback

```python
def get_range_bars(symbol: str, start: str, end: str, include_microstructure: bool = False):
    """Get range bars with cache validation."""
    # Try cache first
    cached_df = cache.get_cached_bars(symbol, start, end)

    if cached_df is not None:
        validation = validate_cached_df(cached_df, include_microstructure)
        if validation.valid:
            return cached_df
        else:
            logger.warning(f"Cache invalid: {validation.reason}, recomputing...")

    # Recompute and cache
    df = compute_range_bars(symbol, start, end, include_microstructure)
    cache.store_bars(df)
    return df
```

## Pattern 4: ALTER TABLE Migrations

**Schema evolution without data loss**: Add columns to existing tables.

### Adding New Columns

```sql
-- Add microstructure columns (v7.0 migration)
ALTER TABLE cache.range_bars
    ADD COLUMN ofi Float64 DEFAULT 0,
    ADD COLUMN vwap_close_deviation Float64 DEFAULT 0,
    ADD COLUMN kyle_lambda_proxy Float64 DEFAULT 0;
```

### Renaming Columns

```sql
-- Rename column (v7.2 migration)
ALTER TABLE cache.range_bars
    RENAME COLUMN aggregation_efficiency TO aggregation_density;
```

### Changing Default Values

```sql
-- Modify default (doesn't affect existing rows)
ALTER TABLE cache.range_bars
    MODIFY COLUMN ofi Float64 DEFAULT nan;
```

### Migration Script Pattern

```sql
-- Migration: v7.0 to v7.2
-- File: migrations/007_002_rename_efficiency.sql

-- Check if column exists (idempotent)
SELECT count() FROM system.columns
WHERE database = 'cache'
  AND table = 'range_bars'
  AND name = 'aggregation_efficiency';

-- Run only if exists:
ALTER TABLE cache.range_bars
    RENAME COLUMN aggregation_efficiency TO aggregation_density;
```

### Python Migration Helper

```python
def ensure_schema_version(client, target_version: int):
    """Apply migrations up to target version."""
    current = get_schema_version(client)

    migrations = {
        2: "ALTER TABLE cache.range_bars ADD COLUMN ofi Float64 DEFAULT 0",
        3: "ALTER TABLE cache.range_bars RENAME COLUMN efficiency TO density",
    }

    for version in range(current + 1, target_version + 1):
        if version in migrations:
            client.command(migrations[version])
            logger.info(f"Applied migration {version}")

    set_schema_version(client, target_version)
```

## Decision Matrix: Which Pattern to Use

| Scenario                            | Recommended Pattern                | Rationale                                 |
| ----------------------------------- | ---------------------------------- | ----------------------------------------- |
| New columns, old data still valid   | ALTER TABLE + Content validation   | Preserve existing cache, validate at read |
| Algorithm changed, old data invalid | Schema version + Filter            | Old data served until recomputed          |
| Frequent schema changes             | Content-based validation           | No version tracking overhead              |
| Large cache, expensive recompute    | ReplacingMergeTree + Incremental   | Automatic dedup, recompute on-demand      |
| Critical correctness                | Schema version + Strict filter     | Reject all data below current version     |
| Multi-team consumers                | Schema version (explicit contract) | Teams can pin to known-good versions      |

## Anti-Patterns

### 1. Silent NULL Propagation

**Problem**: New columns default to NULL, ML models train on incomplete data.

```sql
-- WRONG: No default, returns NULL
ALTER TABLE cache.range_bars ADD COLUMN kyle_lambda Float64;
```

**Fix**: Always specify meaningful defaults or validate at read time.

```sql
-- CORRECT: Explicit default
ALTER TABLE cache.range_bars ADD COLUMN kyle_lambda Float64 DEFAULT 0;
```

### 2. Unbounded Cache Growth

**Problem**: Multiple schema versions accumulate without cleanup.

```python
# WRONG: No TTL or version cleanup
def store_bars(df):
    df['version'] = CURRENT_VERSION
    client.insert_df('cache.range_bars', df)  # Old versions accumulate forever
```

**Fix**: Use ReplacingMergeTree or periodic cleanup.

```sql
-- Cleanup old versions (run periodically)
-- Pass cutoff_ts as a Python-computed UTC timestamp literal, not now()
ALTER TABLE cache.range_bars DELETE
WHERE schema_version < %(min_version)s
  AND computed_at < %(cutoff_ts)s
SETTINGS mutations_sync = 1;
```

### 3. Version-Only Without Content Check

**Problem**: Version matches but data is corrupted or incomplete.

```python
# WRONG: Trust version blindly
if cached_df['schema_version'].iloc[0] >= CURRENT_VERSION:
    return cached_df  # May have NULL microstructure columns
```

**Fix**: Combine version filter with content validation.

```python
# CORRECT: Version + content validation
if cached_df['schema_version'].iloc[0] >= CURRENT_VERSION:
    validation = validate_cached_df(cached_df, include_microstructure=True)
    if validation.valid:
        return cached_df
```

### 4. Breaking Changes Without Migration Path

**Problem**: Column rename breaks all existing queries.

```sql
-- WRONG: Rename without transition period
ALTER TABLE cache.range_bars
    RENAME COLUMN threshold_bps TO threshold_decimal_bps;
-- All queries using threshold_bps immediately fail
```

**Fix**: Add new column, migrate, then remove old.

```sql
-- CORRECT: Additive migration
ALTER TABLE cache.range_bars ADD COLUMN threshold_decimal_bps UInt32;
ALTER TABLE cache.range_bars UPDATE threshold_decimal_bps = threshold_bps WHERE 1;
-- Application migrates to new column
-- Later: ALTER TABLE cache.range_bars DROP COLUMN threshold_bps;
```

## Complete Example: rangebar-py Cache

```sql
-- Production schema with all evolution patterns
CREATE TABLE IF NOT EXISTS rangebar_cache.range_bars (
    -- Primary key columns
    symbol LowCardinality(String),
    threshold_decimal_bps UInt32,
    timestamp_ms Int64,

    -- OHLCV (always present)
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,

    -- Microstructure (v7.0+, DEFAULT for backward compat)
    ofi Float64 DEFAULT 0,
    vwap_close_deviation Float64 DEFAULT 0,
    kyle_lambda_proxy Float64 DEFAULT 0,
    trade_intensity Float64 DEFAULT 0,

    -- Evolution tracking
    cache_key String,                        -- Content hash
    rangebar_version String DEFAULT '',      -- Application version
    computed_at DateTime64(3) DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(computed_at)
PARTITION BY (symbol, threshold_decimal_bps, toYYYYMM(toDateTime(timestamp_ms / 1000)))
ORDER BY (symbol, threshold_decimal_bps, timestamp_ms);
```

```python
# Python client with full validation
from rangebar.constants import MICROSTRUCTURE_COLUMNS
from importlib.metadata import version as pkg_version

class RangeBarCache:
    # SSoT-OK: Version read from package metadata at runtime
    CURRENT_VERSION = pkg_version("rangebar")

    def get_cached_bars(self, symbol: str, start_ms: int, end_ms: int,
                        include_microstructure: bool = False) -> pd.DataFrame | None:
        """Get cached bars with schema validation."""
        df = self._query_bars(symbol, start_ms, end_ms)

        if df is None or df.empty:
            return None

        # Content-based validation
        if include_microstructure:
            for col in MICROSTRUCTURE_COLUMNS:
                if col not in df.columns:
                    logger.warning(f"Cache missing {col}, invalidating")
                    return None
                if df[col].isnull().all() or (df[col] == 0).all():
                    logger.warning(f"Cache has empty {col}, invalidating")
                    return None

        return df

    def store_bars(self, df: pd.DataFrame, symbol: str,
                   threshold_decimal_bps: int) -> int:
        """Store bars with version metadata."""
        df = df.copy()
        df['rangebar_version'] = self.CURRENT_VERSION
        df['computed_at'] = pd.Timestamp.now()

        # Add optional microstructure columns if present
        columns = ['timestamp_ms', 'open', 'high', 'low', 'close', 'volume']
        for col in MICROSTRUCTURE_COLUMNS:
            if col in df.columns:
                columns.append(col)

        return self.client.insert_df('rangebar_cache.range_bars', df[columns])
```

## Validation Query

Check schema evolution health:

```sql
-- Check version distribution in cache
SELECT
    rangebar_version,
    count() AS row_count,
    min(computed_at) AS oldest,
    max(computed_at) AS newest
FROM rangebar_cache.range_bars
GROUP BY rangebar_version
ORDER BY newest DESC;

-- Check for NULL microstructure columns (indicates stale data)
SELECT
    symbol,
    threshold_decimal_bps,
    count() AS total_rows,
    countIf(ofi = 0 AND vwap_close_deviation = 0) AS missing_microstructure,
    round(missing_microstructure / total_rows * 100, 2) AS pct_missing
FROM rangebar_cache.range_bars
GROUP BY symbol, threshold_decimal_bps
HAVING pct_missing > 50
ORDER BY pct_missing DESC;
```

## Related References

- [Schema Design Workflow](./schema-design-workflow.md) - Initial schema creation
- [Anti-Patterns and Fixes](./anti-patterns-and-fixes.md) - Common ClickHouse mistakes
- [Idiomatic Architecture](./idiomatic-architecture.md) - ReplacingMergeTree patterns
