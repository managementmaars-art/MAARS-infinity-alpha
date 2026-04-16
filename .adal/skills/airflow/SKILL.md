---
name: airflow
cluster: data-engineering
description: "Open-source platform for authoring, scheduling, and monitoring data pipelines programmatically."
tags: ["airflow","orchestration","scheduling"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "airflow workflow orchestration scheduling dag pipeline data engineering"
---

# airflow

## Purpose
Airflow is an open-source workflow orchestration tool for defining, scheduling, and monitoring data pipelines as code. It uses Python to create Directed Acyclic Graphs (DAGs) that represent task dependencies and execution flows.

## When to Use
Use Airflow for scenarios involving recurring data tasks, such as ETL processes, batch jobs, or complex workflows with dependencies. It's ideal when you need dynamic scheduling, retries, and monitoring in data engineering pipelines, especially for production-scale operations with tools like Spark or databases.

## Key Capabilities
- Define workflows as DAGs in Python, specifying tasks, dependencies, and schedules.
- Built-in schedulers that run tasks at defined intervals (e.g., cron-style).
- Web UI for real-time monitoring, including task logs and DAG status via endpoints like `/admin/`.
- Operators like `BashOperator` for shell commands or `PythonOperator` for custom functions.
- Extensible hooks for integrations, such as `PostgresHook` for database connections.
- Configuration via `airflow.cfg` file, e.g., set `[core] executor = LocalExecutor` for local testing.

## Usage Patterns
To use Airflow, install it via `pip install apache-airflow`, then initialize the database with `airflow db init`. Define DAGs in the `dags` folder of your Airflow home directory. Always use a virtual environment to avoid conflicts. For authentication, set environment variables like `$AIRFLOW_UID` for user isolation.

- **Pattern 1**: For scheduled ETL, create a DAG that runs daily, using sensors to wait for data inputs.
- **Pattern 2**: Chain tasks with dependencies, e.g., run a Python script only after a database query succeeds.
- **Example 1**: Define a simple DAG for daily backups:
  ```
  from airflow import DAG
  from airflow.operators.bash import BashOperator
  dag = DAG('daily_backup', schedule_interval='@daily')
  task = BashOperator(task_id='backup', bash_command='mysqldump db > backup.sql', dag=dag)
  ```
- **Example 2**: Schedule a pipeline that processes data with Spark:
  ```
  from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
  task = SparkSubmitOperator(task_id='spark_job', application='/path/to/script.py', dag=dag)
  ```

## Common Commands/API
Run Airflow from the command line after setting up your environment. Use `$AIRFLOW__CORE__FERNET_KEY` for encrypted connections if needed.

- **CLI Commands**:
  - Initialize database: `airflow db init --with-db-init`
  - Start webserver: `airflow webserver --port 8080`
  - Run scheduler: `airflow scheduler --dag-id my_dag`
  - Trigger a DAG: `airflow dags trigger my_dag --conf '{"key":"value"}'`
  - List DAGs: `airflow dags list`

- **API Endpoints** (via REST API, enabled in `airflow.cfg` with `[api] auth_backend = airflow.api.auth.backend.default`):
  - GET `/api/v1/dags` to list all DAGs, requires authentication via API token set as `$AIRFLOW_API_TOKEN`.
  - POST `/api/v1/dags/{dag_id}/dagRuns` to trigger a DAG run, e.g., with JSON payload `{"conf": {"param": "value"}}`.
  - Example snippet for API call using requests:
    ```
    import requests
    response = requests.get('http://localhost:8080/api/v1/dags', headers={'Authorization': f'Bearer {os.environ["AIRFLOW_API_TOKEN"]}'})
    print(response.json())
    ```

## Integration Notes
Integrate Airflow with other tools via hooks and operators. For secrets, use Airflow's Variables or Connections, stored in the metadata database. Set environment variables like `$AIRFLOW_CONN_POSTGRES_DEFAULT` for database connections (e.g., `postgresql://user:pass@localhost/db`).

- Integrate with Spark: Use `SparkSubmitOperator` and set executor configs in the operator, e.g., `conf={"spark.executor.memory": "4g"}`.
- Integrate with AWS: Use `S3Hook` for file operations; set `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` as env vars.
- For Kubernetes, configure `[kubernetes] namespace = default` in `airflow.cfg` and use `KubernetesPodOperator`.

## Error Handling
Handle errors by configuring retries in task definitions, e.g., `retries=3, retry_delay=timedelta(minutes=5)`. Check logs via the Web UI or `airflow tasks logs <dag_id> <task_id>`. Use `on_failure_callback` in DAGs to trigger alerts.

- Common errors: Task failures due to dependencies; fix by ensuring prerequisites like database connections are set.
- Prescriptive steps: In a task, add `email_on_failure=True` and set `[smtp] smtp_host = your.smtp.server` in `airflow.cfg`.
- Example: Define a task with error handling:
  ```
  from airflow.utils.email import send_email
  task = PythonOperator(task_id='failing_task', python_callable=my_function, on_failure_callback=lambda context: send_email('admin@example.com', 'Task Failed', 'Error details'))
  ```

## Graph Relationships
- Related to: spark (for task execution in data pipelines), hadoop (for distributed processing integration), and database tools (for metadata storage).
- Depends on: scheduler components and external hooks like postgres or s3.
- Integrates with: orchestration tools in the data-engineering cluster, such as for combined workflows with ETL frameworks.
