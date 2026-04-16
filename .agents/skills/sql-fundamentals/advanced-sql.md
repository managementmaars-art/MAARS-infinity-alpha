---
name: advanced-sql
description: Master advanced SQL including complex joins, correlated subqueries, CTEs, window functions, and query optimization. Learn sophisticated patterns for complex data analysis.
---

# Advanced SQL

## Subqueries

```sql
-- Scalar subquery (returns single value)
SELECT first_name, salary,
       (SELECT AVG(salary) FROM employees) as avg_salary
FROM employees;

-- Column subquery (returns multiple values)
SELECT first_name FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- IN with subquery
SELECT * FROM employees
WHERE department_id IN (
  SELECT id FROM departments
  WHERE location = 'New York'
);

-- Correlated subquery (references outer query)
SELECT e1.first_name, e1.salary
FROM employees e1
WHERE salary > (
  SELECT AVG(e2.salary)
  FROM employees e2
  WHERE e2.department_id = e1.department_id
);
```

## Common Table Expressions (CTEs)

```sql
-- Basic CTE
WITH high_earners AS (
  SELECT first_name, salary
  FROM employees
  WHERE salary > 80000
)
SELECT * FROM high_earners
WHERE salary > 100000;

-- Multiple CTEs
WITH department_stats AS (
  SELECT department_id, AVG(salary) as avg_salary
  FROM employees
  GROUP BY department_id
),
high_salary_depts AS (
  SELECT department_id
  FROM department_stats
  WHERE avg_salary > 75000
)
SELECT e.*
FROM employees e
WHERE e.department_id IN (SELECT department_id FROM high_salary_depts);

-- Recursive CTE (hierarchical data)
WITH RECURSIVE org_hierarchy AS (
  SELECT id, name, manager_id, 0 as level
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  SELECT e.id, e.name, e.manager_id, oh.level + 1
  FROM employees e
  INNER JOIN org_hierarchy oh ON e.manager_id = oh.id
)
SELECT * FROM org_hierarchy;
```

## Window Functions

```sql
-- ROW_NUMBER - Sequential ranking
SELECT
  first_name,
  salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;

-- RANK - With ties handling
SELECT
  first_name,
  salary,
  RANK() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;

-- DENSE_RANK - Consecutive ranking
SELECT
  first_name,
  salary,
  DENSE_RANK() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;

-- Running sum by partition
SELECT
  department_id,
  first_name,
  salary,
  SUM(salary) OVER (
    PARTITION BY department_id
    ORDER BY hire_date
  ) as cumulative_salary
FROM employees;

-- LAG and LEAD (previous/next rows)
SELECT
  first_name,
  salary,
  LAG(salary) OVER (ORDER BY hire_date) as prev_salary,
  LEAD(salary) OVER (ORDER BY hire_date) as next_salary
FROM employees;

-- FIRST_VALUE and LAST_VALUE
SELECT
  department_id,
  first_name,
  salary,
  FIRST_VALUE(salary) OVER (
    PARTITION BY department_id
    ORDER BY hire_date
  ) as first_salary_in_dept,
  LAST_VALUE(salary) OVER (
    PARTITION BY department_id
    ORDER BY hire_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  ) as last_salary_in_dept
FROM employees;
```

## Advanced JOINs

```sql
-- FULL OUTER JOIN (all from both tables)
SELECT e.first_name, d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;

-- SELF JOIN (join table to itself)
SELECT e1.first_name as employee, e2.first_name as manager
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.id;

-- CROSS JOIN (Cartesian product)
SELECT e.first_name, p.project_name
FROM employees e
CROSS JOIN projects p;

-- Multiple joins with conditions
SELECT e.first_name, d.department_name, p.project_name, t.hours
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
INNER JOIN assignments p ON e.id = p.employee_id
INNER JOIN timesheets t ON p.id = t.assignment_id
WHERE t.hours > 0;
```

## UNION and Set Operations

```sql
-- UNION (remove duplicates)
SELECT first_name, 'Employee' as type FROM employees
UNION
SELECT name, 'Contractor' as type FROM contractors;

-- UNION ALL (keep duplicates)
SELECT first_name FROM employees
UNION ALL
SELECT first_name FROM former_employees;

-- INTERSECT (common rows)
SELECT first_name FROM employees
INTERSECT
SELECT first_name FROM managers;

-- EXCEPT (rows in first but not second)
SELECT first_name FROM employees
EXCEPT
SELECT first_name FROM on_leave_employees;
```

## Complex Aggregations

```sql
-- Multiple aggregations
SELECT
  department_id,
  COUNT(*) as emp_count,
  SUM(salary) as total_salary,
  AVG(salary) as avg_salary,
  MIN(salary) as min_salary,
  MAX(salary) as max_salary
FROM employees
GROUP BY department_id;

-- CASE in aggregation
SELECT
  department_id,
  COUNT(CASE WHEN salary > 75000 THEN 1 END) as high_earners,
  COUNT(CASE WHEN salary BETWEEN 50000 AND 75000 THEN 1 END) as mid_earners,
  COUNT(CASE WHEN salary < 50000 THEN 1 END) as low_earners
FROM employees
GROUP BY department_id;

-- Conditional aggregation
SELECT
  department_id,
  SUM(CASE WHEN salary > 75000 THEN salary ELSE 0 END) as high_salary_total,
  AVG(CASE WHEN salary > 75000 THEN salary END) as high_salary_avg
FROM employees
GROUP BY department_id;
```

## Query Optimization Tips

1. **Index Usage**: Use indexes on columns in WHERE clauses, JOINs, and ORDER BY
2. **Avoid SELECT ***: Specify only needed columns
3. **Filter Early**: Use WHERE before JOINs when possible
4. **Limit Results**: Use LIMIT when you don't need all rows
5. **Use EXPLAIN**: Check query execution plans
6. **Avoid Correlated Subqueries**: Replace with JOINs when possible
7. **Proper JOIN Order**: Join smaller result sets first

## Performance Analysis

```sql
-- View query execution plan
EXPLAIN SELECT * FROM employees WHERE salary > 50000;

-- Analyze slowness
EXPLAIN ANALYZE SELECT * FROM employees
JOIN departments ON employees.department_id = departments.id
WHERE employees.salary > 75000;
```
