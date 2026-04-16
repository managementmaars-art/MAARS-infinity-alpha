---
name: etl-pipelines
description: ETL and data pipeline design including extract, transform, load operations, incremental loading, error handling, scheduling, and modern data engineering patterns.
---

# ETL & Data Pipelines

## Extract Patterns

### From Relational Databases

```sql
-- Full extract of source table
SELECT * FROM source_system.customers;

-- Incremental extract using timestamp
SELECT *
FROM source_system.orders
WHERE updated_timestamp > (
  SELECT MAX(last_sync_time)
  FROM pipeline_control.sync_status
  WHERE source_table = 'orders'
);

-- Change Data Capture (CDC) simulation
CREATE TABLE source.orders_cdc (
  order_id INT,
  customer_id INT,
  amount DECIMAL(12, 2),
  operation_type VARCHAR(1),  -- 'I' = Insert, 'U' = Update, 'D' = Delete
  operation_timestamp TIMESTAMP
);

-- Extract only changed records
SELECT *
FROM source.orders_cdc
WHERE operation_timestamp >= (
  SELECT MAX(last_processed_time)
  FROM pipeline_control.cdc_status
)
ORDER BY operation_timestamp;
```

### From APIs and Streaming

```python
# Pseudocode for API extraction
def extract_from_api():
    url = "https://api.example.com/data"
    headers = {"Authorization": f"Bearer {api_token}"}

    # Incremental extraction with cursor
    last_cursor = get_last_cursor()

    params = {
        "limit": 1000,
        "cursor": last_cursor
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Save extracted data
    save_to_raw_storage(data)

    # Update cursor for next run
    save_cursor(data['next_cursor'])

    return data
```

## Transform Patterns

### Data Cleaning

```sql
-- Standardize and clean data
SELECT
  UPPER(TRIM(first_name)) as first_name,
  UPPER(TRIM(last_name)) as last_name,
  LOWER(TRIM(email)) as email,
  COALESCE(phone, 'Unknown') as phone,
  CASE
    WHEN LENGTH(phone) < 10 THEN NULL
    ELSE phone
  END as cleaned_phone,
  -- Remove duplicates
  ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_date DESC) as row_num
FROM raw_customers
WHERE first_name IS NOT NULL
  AND email IS NOT NULL
HAVING ROW_NUMBER() = 1;
```

### Data Validation

```sql
-- Validation queries during transformation
SELECT
  'Email format' as validation,
  COUNT(*) as failed_count
FROM raw_customers
WHERE email NOT LIKE '%@%.%'

UNION ALL

SELECT
  'Missing required fields',
  COUNT(*)
FROM raw_customers
WHERE first_name IS NULL
  OR last_name IS NULL
  OR email IS NULL

UNION ALL

SELECT
  'Salary out of range',
  COUNT(*)
FROM raw_employees
WHERE salary < 0 OR salary > 10000000;
```

### Complex Transformations

```sql
-- Multi-step transformation with CTEs
WITH raw_data AS (
  -- Step 1: Extract and clean
  SELECT
    customer_id,
    order_id,
    CAST(amount AS DECIMAL(12, 2)) as amount,
    CAST(order_date AS DATE) as order_date
  FROM raw_orders
  WHERE amount > 0 AND order_date IS NOT NULL
),
aggregated_data AS (
  -- Step 2: Aggregate
  SELECT
    customer_id,
    DATE_TRUNC('month', order_date)::DATE as month,
    COUNT(DISTINCT order_id) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
  FROM raw_data
  GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
enriched_data AS (
  -- Step 3: Enrich with business logic
  SELECT
    customer_id,
    month,
    transaction_count,
    total_amount,
    avg_amount,
    CASE
      WHEN total_amount > 10000 THEN 'High Value'
      WHEN total_amount > 1000 THEN 'Medium Value'
      ELSE 'Low Value'
    END as customer_value_segment,
    CURRENT_TIMESTAMP as load_timestamp
  FROM aggregated_data
)
INSERT INTO transformed_customer_monthly
SELECT * FROM enriched_data;
```

## Load Patterns

### Append Load (Full)

```sql
-- Simple append - add all new records
INSERT INTO fact_sales
SELECT
  sale_id,
  date_id,
  customer_id,
  product_id,
  amount,
  CURRENT_TIMESTAMP as load_time
FROM staging_sales
WHERE load_status = 'Ready';

-- Update load control
UPDATE pipeline_control.load_status
SET last_load_time = CURRENT_TIMESTAMP,
    record_count = (SELECT COUNT(*) FROM staging_sales),
    status = 'Completed'
WHERE pipeline_name = 'fact_sales_load';
```

### Incremental Load (Upsert)

```sql
-- Insert or update strategy using MERGE (or UPSERT if supported)
MERGE INTO fact_customer_monthly t
USING staging_customer_monthly s
ON t.customer_id = s.customer_id
  AND t.month = s.month
WHEN MATCHED THEN
  UPDATE SET
    transaction_count = s.transaction_count,
    total_sales = s.total_sales,
    updated_date = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
  INSERT (customer_id, month, transaction_count, total_sales, created_date, updated_date)
  VALUES (s.customer_id, s.month, s.transaction_count, s.total_sales,
          CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- For databases without MERGE:
-- Step 1: Delete existing records
DELETE FROM fact_customer_monthly
WHERE (customer_id, month) IN (
  SELECT customer_id, month FROM staging_customer_monthly
);

-- Step 2: Insert new records
INSERT INTO fact_customer_monthly
SELECT * FROM staging_customer_monthly;
```

### Dimension Load (SCD Type 2)

```sql
-- Slowly Changing Dimension - Type 2 (versioning)

-- Step 1: Identify changes
WITH changes AS (
  SELECT
    s.customer_id,
    s.email,
    s.phone,
    s.address,
    s.city,
    d.email as old_email,
    d.phone as old_phone,
    d.address as old_address,
    d.city as old_city,
    CASE
      WHEN s.email != d.email OR s.phone != d.phone
        OR s.address != d.address OR s.city != d.city
      THEN TRUE
      ELSE FALSE
    END as has_changes
  FROM staging_customers s
  LEFT JOIN dim_customer d ON s.customer_id = d.customer_id
    AND d.is_current = TRUE
)
-- Step 2: Close old records for customers with changes
UPDATE dim_customer
SET is_current = FALSE,
    end_date = CURRENT_DATE - INTERVAL '1 day'
WHERE customer_id IN (
  SELECT customer_id FROM changes WHERE has_changes = TRUE
)
AND is_current = TRUE;

-- Step 3: Insert new versions
INSERT INTO dim_customer (
  customer_id, email, phone, address, city,
  effective_date, end_date, is_current,
  created_date, updated_date
)
SELECT
  s.customer_id,
  s.email,
  s.phone,
  s.address,
  s.city,
  CURRENT_DATE,
  NULL,
  TRUE,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
FROM staging_customers s
WHERE s.customer_id NOT IN (
  SELECT DISTINCT customer_id FROM dim_customer WHERE is_current = TRUE
);
```

## Pipeline Orchestration

### Control Framework

```sql
-- Pipeline execution log table
CREATE TABLE pipeline_control.execution_log (
  execution_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  pipeline_name VARCHAR(100),
  step_name VARCHAR(100),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(20),  -- 'Running', 'Success', 'Failed'
  record_count INT,
  error_message TEXT,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track last successful load
CREATE TABLE pipeline_control.load_watermark (
  pipeline_name VARCHAR(100) PRIMARY KEY,
  last_successful_load TIMESTAMP,
  records_processed INT,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mark pipeline start
INSERT INTO pipeline_control.execution_log
(pipeline_name, step_name, start_time, status)
VALUES ('customer_etl', 'extract', CURRENT_TIMESTAMP, 'Running');

-- Update on completion
UPDATE pipeline_control.execution_log
SET
  end_time = CURRENT_TIMESTAMP,
  status = 'Success',
  record_count = (SELECT COUNT(*) FROM staging_customers)
WHERE execution_id = @current_exec_id;
```

### Error Handling

```python
# Pseudocode for ETL error handling
def run_etl_pipeline():
    execution_id = log_pipeline_start('customer_etl')

    try:
        # Extract
        raw_data = extract_data()
        log_step(execution_id, 'extract', 'Success', len(raw_data))

        # Transform
        clean_data = transform_data(raw_data)
        validate_data(clean_data)
        log_step(execution_id, 'transform', 'Success', len(clean_data))

        # Load
        load_data(clean_data)
        log_step(execution_id, 'load', 'Success', len(clean_data))

        log_pipeline_completion(execution_id, 'Success')

    except ValidationError as e:
        log_error(execution_id, 'validation', str(e))
        send_alert(f"ETL failed: {e}")
        rollback_transaction()

    except DatabaseError as e:
        log_error(execution_id, 'database', str(e))
        send_alert(f"Database error: {e}")
        retry_with_backoff()
```

## Performance Optimization

```sql
-- Batch processing for large volumes
-- Instead of: INSERT INTO target SELECT * FROM source (slow for millions)

-- Do: Process in batches
DECLARE @batch_size INT = 100000;
DECLARE @offset INT = 0;
DECLARE @total INT = (SELECT COUNT(*) FROM source_table);

WHILE @offset < @total
BEGIN
  INSERT INTO target_table
  SELECT * FROM source_table
  LIMIT @batch_size OFFSET @offset;

  SET @offset = @offset + @batch_size;
END;

-- Parallel processing
-- Process multiple dimensions in parallel
-- Fact table load only after all dimensions complete

-- Compression and partitioning
CREATE TABLE large_fact_table (
  date_id INT,
  customer_id INT,
  amount DECIMAL(12, 2)
)
PARTITION BY RANGE (YEAR(date_id)) (
  PARTITION p_2022 VALUES LESS THAN (2023),
  PARTITION p_2023 VALUES LESS THAN (2024),
  PARTITION p_2024 VALUES LESS THAN (2025),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Create indexes on load columns
CREATE INDEX idx_staging_sales_date ON staging_sales(load_date);
```

## Best Practices Checklist

✅ Implement comprehensive error logging and alerting
✅ Use staging tables for intermediate transformations
✅ Version your data transformations
✅ Implement data quality checks at each stage
✅ Use idempotent operations (safe to run multiple times)
✅ Implement recovery procedures for failed loads
✅ Monitor pipeline performance metrics
✅ Use partitioning for large tables
✅ Implement incremental loads where possible
✅ Document data lineage and transformations
