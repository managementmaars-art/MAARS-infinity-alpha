---
name: sql-expert
description: SQL expert patterns — window functions, CTEs, query optimization, indexes, partitioning, analytics queries, PostgreSQL/MySQL/SQLite for MAARS data agents
---

# SQL Expert — MAARS Reference

## Window Functions
```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT
    user_id,
    order_date,
    amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) AS order_num,
    RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS amount_rank,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date 
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
    AVG(amount) OVER (PARTITION BY user_id 
                      ORDER BY order_date
                      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3_avg,
    LAG(amount, 1) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_amount,
    LEAD(amount, 1) OVER (PARTITION BY user_id ORDER BY order_date) AS next_amount,
    FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS first_order,
    LAST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY order_date
                              ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS last_order,
    NTILE(4) OVER (ORDER BY amount) AS quartile
FROM orders;
```

## CTEs (Common Table Expressions)
```sql
-- Recursive CTE for hierarchies
WITH RECURSIVE org_tree AS (
    -- Anchor
    SELECT id, name, manager_id, 0 AS level, CAST(name AS VARCHAR(1000)) AS path
    FROM employees WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive
    SELECT e.id, e.name, e.manager_id, t.level + 1,
           CONCAT(t.path, ' > ', e.name)
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY path;

-- Multiple CTEs for complex analysis
WITH
monthly_revenue AS (
    SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS revenue
    FROM orders WHERE status = 'completed'
    GROUP BY 1
),
prev_month AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly_revenue
)
SELECT month, revenue,
       prev_revenue,
       ROUND((revenue - prev_revenue) / prev_revenue * 100, 2) AS mom_growth_pct
FROM prev_month
ORDER BY month;
```

## Analytics Queries

### Cohort Retention
```sql
WITH cohorts AS (
    SELECT user_id, DATE_TRUNC('month', MIN(created_at)) AS cohort_month
    FROM users GROUP BY user_id
),
activity AS (
    SELECT user_id, DATE_TRUNC('month', activity_date) AS activity_month
    FROM user_activity
),
cohort_data AS (
    SELECT 
        c.cohort_month,
        EXTRACT(MONTH FROM AGE(a.activity_month, c.cohort_month)) AS month_number,
        COUNT(DISTINCT a.user_id) AS users
    FROM cohorts c
    JOIN activity a ON c.user_id = a.user_id
    GROUP BY 1, 2
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM cohorts GROUP BY 1
)
SELECT 
    d.cohort_month,
    d.month_number,
    d.users,
    cs.cohort_size,
    ROUND(d.users::numeric / cs.cohort_size * 100, 1) AS retention_pct
FROM cohort_data d
JOIN cohort_sizes cs ON d.cohort_month = cs.cohort_month
ORDER BY 1, 2;
```

### Funnel Analysis
```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'signup' THEN 1 ELSE 0 END) AS signed_up,
        MAX(CASE WHEN event = 'onboarding_complete' THEN 1 ELSE 0 END) AS onboarded,
        MAX(CASE WHEN event = 'first_purchase' THEN 1 ELSE 0 END) AS purchased
    FROM events
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    COUNT(*) AS total_users,
    SUM(signed_up) AS signed_up,
    SUM(onboarded) AS onboarded,
    SUM(purchased) AS purchased,
    ROUND(SUM(onboarded)::numeric / SUM(signed_up) * 100, 1) AS signup_to_onboard_pct,
    ROUND(SUM(purchased)::numeric / SUM(onboarded) * 100, 1) AS onboard_to_purchase_pct
FROM funnel;
```

## Query Optimization
```sql
-- EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- Index types (PostgreSQL)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);  -- B-tree (default)
CREATE INDEX idx_events_payload ON events USING gin(payload);     -- GIN for JSONB
CREATE INDEX idx_articles_fts ON articles USING gin(to_tsvector('english', content)); -- Full-text
CREATE INDEX idx_orders_created ON orders(created_at DESC) WHERE status = 'completed'; -- Partial
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));       -- Expression

-- Avoid full scans
-- BAD: function on indexed column
WHERE LOWER(email) = 'user@example.com'
-- GOOD: use expression index or store normalized
WHERE email = LOWER('User@Example.com')

-- Covering index (all needed columns in index)
CREATE INDEX idx_orders_covering ON orders(user_id) INCLUDE (amount, status, created_at);
```

## JSON in PostgreSQL
```sql
-- JSONB operations
SELECT data->>'name' AS name,                    -- text
       (data->>'age')::int AS age,               -- cast
       data->'address'->>'city' AS city,         -- nested
       data @> '{"role": "admin"}' AS is_admin   -- contains

FROM users WHERE data ? 'email';                  -- has key

-- Array of JSONB
SELECT id, item
FROM orders, jsonb_array_elements(line_items) AS item
WHERE (item->>'price')::numeric > 100;

-- Aggregate to JSONB
SELECT user_id, jsonb_agg(jsonb_build_object(
    'id', id, 'amount', amount, 'date', created_at
) ORDER BY created_at) AS orders
FROM orders GROUP BY user_id;

-- Update JSONB field
UPDATE users SET data = data || '{"verified": true}' WHERE id = 123;
UPDATE users SET data = data - 'temp_field' WHERE id = 123;  -- remove key
```

## Partitioning
```sql
-- Range partitioning by date
CREATE TABLE events (
    id BIGSERIAL,
    user_id BIGINT,
    event_name TEXT,
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE events_2025 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Queries automatically use partition pruning
SELECT * FROM events WHERE created_at >= '2025-01-01';  -- only scans events_2025
```

## Models to Use
- **Complex query writing**: `claude-opus-4-6` (best SQL reasoning)
- **Query optimization**: `claude-opus-4-6` (explain plan interpretation)
- **Schema design**: `claude-sonnet-4-6`
- **Data analysis queries**: `gpt-4o` with code interpreter
