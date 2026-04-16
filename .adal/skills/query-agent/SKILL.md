---
name: query-agent
description: Natural language to SQL query agent with schema discovery and XML result export. Use when an agent needs to (1) discover and interpret database schemas, (2) convert natural language questions into SQL queries using LLM, (3) execute queries securely, and (4) export results as XML to configurable storage (Google Drive, S3, local, etc.). Fully configurable via environment variables.
---

# Query Agent Skill

Query databases using natural language and export results as XML to configurable storage.

## Quick Start

```python
from query_agent import query
import os

# Database connection (secure SSL supported)
os.environ["DB_HOST"] = "db.example.com"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "pass"
os.environ["DB_SSL_MODE"] = "require"

# LLM configuration
os.environ["LLM_API_BASE"] = "https://api.openai.com/v1"
os.environ["LLM_MODEL"] = "gpt-4"
os.environ["LLM_API_KEY"] = "sk-..."

# Storage for XML results
os.environ["STORAGE_TYPE"] = "gdrive"  # gdrive, s3, local
os.environ["STORAGE_GDRIVE_CREDENTIALS"] = "./gdrive-credentials.json"

# Query
result = query(
    question="What were the top 10 sales by region in 2023?",
    database="analytics",  # Optional: specific DB
    table_filter=["sales", "regions"]  # Optional: hint which tables to use
)

print(f"SQL: {result['sql']}")
print(f"Rows: {result['row_count']}")
print(f"XML saved to: {result['xml_url']}")
print(f"Summary: {result['summary']}")
```

## Environment Configuration

### Database (Source)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | No | `postgresql` | Database type: postgresql, mysql, sqlite |
| `DB_HOST` | Yes* | - | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | Yes* | - | Database user |
| `DB_PASSWORD` | Yes* | - | Database password |
| `DB_NAME` | No | - | Default database |
| `DB_SSL_MODE` | No | `prefer` | SSL mode for secure connections |
| `DB_SSL_ROOT_CERT` | No | - | CA certificate path |
| `DB_URL` | Alt | - | Full connection string |

### LLM (SQL Generation)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_BASE` | Yes | - | LLM API endpoint |
| `LLM_MODEL` | Yes | - | Model name |
| `LLM_API_KEY` | No | - | API key |
| `LLM_TIMEOUT` | No | `120` | Timeout seconds |

### Storage (XML Export)

| Variable | Required | Description |
|----------|----------|-------------|
| `STORAGE_TYPE` | Yes | `gdrive`, `s3`, `local`, `azure`, `gcs` |
| `STORAGE_PATH_PREFIX` | No | Prefix for output path |

**Google Drive:**
- `STORAGE_GDRIVE_CREDENTIALS` - Path to service account JSON
- `STORAGE_GDRIVE_FOLDER_ID` - Optional folder ID

**S3:**
- `STORAGE_S3_BUCKET` - S3 bucket name
- `STORAGE_S3_PREFIX` - Key prefix
- `STORAGE_S3_REGION` - AWS region
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

**Local:**
- `STORAGE_LOCAL_PATH` - Base directory for files

**Azure Blob:**
- `STORAGE_AZURE_CONNECTION_STRING` - Azure connection
- `STORAGE_AZURE_CONTAINER` - Container name

**Google Cloud Storage:**
- `STORAGE_GCS_BUCKET` - GCS bucket
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account JSON

## Schema Discovery

The agent automatically discovers schema from the database:

```python
from query_agent import discover_schema

# Discover all tables in database
schema = discover_schema(database="production")

# Schema structure:
# {
#   "database": "production",
#   "tables": [
#     {
#       "name": "sales",
#       "description": "Auto-generated from schema",
#       "columns": [
#         {"name": "id", "type": "integer", "nullable": false},
#         {"name": "amount", "type": "float", "nullable": true},
#         {"name": "created_at", "type": "timestamp", "nullable": true}
#       ]
#     }
#   ]
# }
```

## Query Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Natural   │───▶│  Discover   │───▶│   Generate  │
│  Language   │    │   Schema    │    │     SQL     │
│  Question   │    │             │    │    (LLM)    │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│  XML Export │◀───│   Execute   │◀───│   Validate  │
│   to Storage│    │    Query    │    │     SQL     │
└─────────────┘    └─────────────┘    └─────────────┘
```

1. **Discover Schema** - Query database metadata for tables/columns
2. **Generate SQL** - LLM converts question to SQL using schema
3. **Validate** - Check SQL safety (read-only, allowed functions)
4. **Execute** - Run query against database
5. **Export XML** - Convert results to XML and upload to storage
6. **Summarize** - LLM generates natural language summary

## Usage Examples

### Basic Query

```python
from query_agent import query

result = query("Show me total sales by month for 2023")

# Returns:
# {
#   "sql": "SELECT DATE_TRUNC('month', created_at) as month, SUM(amount) as total FROM sales WHERE created_at >= '2023-01-01' GROUP BY month ORDER BY month",
#   "row_count": 12,
#   "xml_path": "gdrive://folder/results_20240205_143022.xml",
#   "xml_url": "https://drive.google.com/...",
#   "summary": "Sales totaled $1.2M for 2023, with peak in December ($150K)",
#   "key_findings": ["December was strongest month", "Q4 showed 20% growth"],
#   "execution_time_seconds": 2.3
# }
```

### Multi-Table Query with Hints

```python
result = query(
    question="What products had the highest returns?",
    database="warehouse",
    table_filter=["orders", "products", "returns"],  # Hint which tables
    storage_path="reports/returns_analysis"  # Custom output path
)
```

### Batch Queries

```python
questions = [
    "Top 10 customers by revenue",
    "Monthly growth rate 2023",
    "Product category performance"
]

results = []
for q in questions:
    result = query(q, database="analytics")
    results.append(result)
    print(f"✓ {result['summary'][:60]}...")
```

## XML Output Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<queryResult>
  <metadata>
    <query>Top 10 customers by revenue</query>
    <sql>SELECT customer_name, SUM(amount) as revenue FROM sales GROUP BY customer_name ORDER BY revenue DESC LIMIT 10</sql>
    <generatedAt>2024-02-05T14:30:22Z</generatedAt>
    <rowCount>10</rowCount>
    <executionTimeMs>245</executionTimeMs>
    <summary>Top customer generated $500K in revenue</summary>
    <keyFindings>
      <finding>Top 3 customers account for 40% of revenue</finding>
      <finding>Average top-10 customer value: $320K</finding>
    </keyFindings>
  </metadata>
  <schema>
    <column name="customer_name" type="string"/>
    <column name="revenue" type="float"/>
  </schema>
  <rows>
    <row>
      <customer_name>Acme Corp</customer_name>
      <revenue>500000.00</revenue>
    </row>
    <row>
      <customer_name>Global Industries</customer_name>
      <revenue>450000.00</revenue>
    </row>
    ...
  </rows>
</queryResult>
```

## Storage URL Formats

| Storage | URL Format | Example |
|---------|------------|---------|
| Google Drive | `gdrive://FILE_ID` | `gdrive://1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms` |
| S3 | `s3://bucket/key` | `s3://results-bucket/queries/2024/data.xml` |
| Local | `file:///path` | `file:///data/results/query_123.xml` |
| Azure | `azure://container/blob` | `azure://data/results.xml` |
| GCS | `gs://bucket/object` | `gs://bucket/results/query.xml` |

## Security

### SQL Safety

- **Read-only**: Only SELECT statements allowed
- **Function whitelist**: SUM, AVG, COUNT, MAX, MIN, ROUND, etc.
- **No DDL**: CREATE, DROP, ALTER blocked
- **No DML**: INSERT, UPDATE, DELETE blocked
- **Row limit**: Max 10,000 rows returned
- **Timeout**: Query timeout (default 30s)

### Secure Connections

```bash
# PostgreSQL with SSL
export DB_SSL_MODE="require"

# With certificate verification
export DB_SSL_MODE="verify-full"
export DB_SSL_ROOT_CERT="./ca-cert.pem"

# Redis cache (if enabled)
export REDIS_URL="rediss://:pass@redis.example.com:6380"
```

## Requirements

```bash
# Core
pip install requests

# Database
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL

# Storage
pip install google-api-python-client google-auth  # Google Drive
pip install boto3            # S3
pip install azure-storage-blob  # Azure
pip install google-cloud-storage  # GCS
```
