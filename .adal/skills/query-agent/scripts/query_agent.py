#!/usr/bin/env python3
"""Natural language to SQL query agent with XML export.

Supports:
- Schema discovery from PostgreSQL/MySQL/SQLite
- LLM-powered SQL generation
- Results export as XML to Google Drive, S3, Azure, GCS, or local
- Fully configurable via environment variables

Usage:
    python query_agent.py "What were total sales by month?"
    
Environment:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    DB_SSL_MODE, DB_SSL_ROOT_CERT
    LLM_API_BASE, LLM_MODEL, LLM_API_KEY
    STORAGE_TYPE, STORAGE_* (per storage type)
"""

import json
import logging
import os
import re
import ssl
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Environment Configuration
# ============================================================================

def get_env(key: str, default: str = None, required: bool = False) -> Optional[str]:
    """Get environment variable."""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Environment variable {key} is required")
    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default).lower()).lower() in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    return int(os.getenv(key, default))


# ============================================================================
# Database Connection (reused from file-ingestion skill)
# ============================================================================

class DatabaseConnection:
    """Database connection manager with SSL support."""
    
    def __init__(self, db_name: str = None):
        self.db_type = get_env("DB_TYPE", "postgresql")
        self.conn = None
        self.target_db = db_name or get_env("DB_NAME")
    
    def _build_connection_params(self, db_name: str = None) -> dict:
        """Build connection parameters with SSL."""
        params = {}
        
        db_url = get_env("DB_URL")
        if db_url:
            params["dsn"] = db_url
            return params
        
        if self.db_type == "sqlite":
            params["database"] = db_name or get_env("DB_NAME", "query.db")
            return params
        
        params["host"] = get_env("DB_HOST", required=True)
        params["port"] = get_env_int("DB_PORT", 5432 if self.db_type == "postgresql" else 3306)
        params["user"] = get_env("DB_USER", required=True)
        params["password"] = get_env("DB_PASSWORD", required=True)
        params["database"] = db_name or get_env("DB_NAME", "postgres" if self.db_type == "postgresql" else "mysql")
        
        # SSL Configuration
        ssl_mode = get_env("DB_SSL_MODE", "prefer")
        if ssl_mode in ("require", "verify-ca", "verify-full"):
            if self.db_type == "postgresql":
                import psycopg2
                params["sslmode"] = ssl_mode
                ca_cert = get_env("DB_SSL_ROOT_CERT")
                if ca_cert:
                    params["sslrootcert"] = ca_cert
            elif self.db_type == "mysql":
                params["ssl"] = ssl.create_default_context()
                ca_cert = get_env("DB_SSL_ROOT_CERT")
                if ca_cert and Path(ca_cert).exists():
                    params["ssl"].load_verify_locations(ca_cert)
        
        return params
    
    def connect(self, db_name: str = None):
        """Connect to database."""
        target = db_name or self.target_db
        
        if self.db_type == "postgresql":
            import psycopg2
            params = self._build_connection_params(target)
            self.conn = psycopg2.connect(**params)
        elif self.db_type == "mysql":
            import pymysql
            params = self._build_connection_params(target)
            self.conn = pymysql.connect(**params)
        elif self.db_type == "sqlite":
            import sqlite3
            params = self._build_connection_params(target)
            self.conn = sqlite3.connect(params["database"])
            self.conn.row_factory = sqlite3.Row
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


def get_db_connection(db_name: str = None):
    """Get database connection."""
    db = DatabaseConnection(db_name)
    return db.connect(db_name), db.db_type


# ============================================================================
# Schema Discovery
# ============================================================================

def discover_schema(database: str = None, table_filter: list = None) -> dict:
    """Discover database schema.
    
    Args:
        database: Database name (optional)
        table_filter: List of table names to filter (optional)
    
    Returns:
        Schema dict with tables and columns
    """
    conn, db_type = get_db_connection(database)
    
    try:
        cursor = conn.cursor()
        tables = []
        
        if db_type == "postgresql":
            # Get tables
            table_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """
            cursor.execute(table_query)
            all_tables = [row[0] for row in cursor.fetchall()]
            
            # Filter tables if specified
            if table_filter:
                all_tables = [t for t in all_tables if t in table_filter]
            
            # Get columns for each table
            for table_name in all_tables:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES"
                    })
                
                tables.append({
                    "name": table_name,
                    "description": f"Table {table_name}",
                    "columns": columns
                })
        
        elif db_type == "mysql":
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            if table_filter:
                all_tables = [t for t in all_tables if t in table_filter]
            
            for table_name in all_tables:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES"
                    })
                
                tables.append({
                    "name": table_name,
                    "description": f"Table {table_name}",
                    "columns": columns
                })
        
        elif db_type == "sqlite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]
            all_tables = [t for t in all_tables if not t.startswith("sqlite_")]
            
            if table_filter:
                all_tables = [t for t in all_tables if t in table_filter]
            
            for table_name in all_tables:
                cursor.execute(f'PRAGMA table_info("{table_name}")')
                columns = []
                for row in cursor.fetchall():
                    columns.append({
                        "name": row[1],
                        "type": row[2],
                        "nullable": not row[3]  # notnull column
                    })
                
                tables.append({
                    "name": table_name,
                    "description": f"Table {table_name}",
                    "columns": columns
                })
        
        cursor.close()
        
        return {
            "database": database or get_env("DB_NAME", "default"),
            "db_type": db_type,
            "tables": tables
        }
    
    finally:
        conn.close()


# ============================================================================
# SQL Generation via LLM
# ============================================================================

SQL_GENERATION_PROMPT = """You are a SQL query generator for a data exploration system.

Your job:
1. Read the user's natural language question
2. Generate a SQL query that answers it using the provided database schema
3. Return valid SQL syntax for the specified database type

Database Schema:
{schema_description}

Database Type: {db_type}

Rules:
- ONLY use tables and columns from the schema above
- Use proper SQL syntax for the database type
- Allowed functions: SUM, AVG, COUNT, MAX, MIN, ROUND, UPPER, LOWER, DATE_TRUNC, EXTRACT, ABS, CEIL, FLOOR, COALESCE, NULLIF
- Disallowed: string_agg, json_agg, window functions, recursive CTEs
- WHERE, GROUP BY, HAVING, ORDER BY, LIMIT allowed
- Max 10000 rows (add LIMIT 10000)
- Max 30 second execution time
- ONLY SELECT statements (no INSERT, UPDATE, DELETE, DROP, ALTER, CREATE)

If the question cannot be answered with available data:
  Return error response explaining what's missing

Output format: ONLY valid JSON with keys:
  - sql: string (valid SQL query) OR null if impossible
  - reasoning: string (why you chose this approach)
  - confidence: float (0.0-1.0, your assessment of query validity)
  - error: string (optional, if query not possible)

Example (success):
{{
  "sql": "SELECT customer_name, SUM(amount) as total FROM sales GROUP BY customer_name ORDER BY total DESC LIMIT 10",
  "reasoning": "User asked for top customers by sales. Grouped by customer, summed amounts, sorted descending.",
  "confidence": 0.95
}}

Example (impossible):
{{
  "sql": null,
  "error": "No customer table available to answer this question",
  "reasoning": "Question requires customer data but schema only has sales table",
  "confidence": 0.1
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""


def _format_schema_for_prompt(schema: dict) -> str:
    """Format schema for LLM prompt."""
    lines = []
    for table in schema["tables"]:
        lines.append(f"\nTable: {table['name']}")
        lines.append(f"  Description: {table['description']}")
        lines.append("  Columns:")
        for col in table["columns"]:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            lines.append(f"    - {col['name']}: {col['type']} ({nullable})")
    return "\n".join(lines)


def generate_sql(question: str, schema: dict) -> dict:
    """Generate SQL from natural language question using LLM.
    
    Args:
        question: Natural language question
        schema: Database schema from discover_schema()
    
    Returns:
        Dict with sql, reasoning, confidence, error
    """
    api_base = get_env("LLM_API_BASE", required=True)
    model = get_env("LLM_MODEL", required=True)
    api_key = get_env("LLM_API_KEY", "")
    timeout = get_env_int("LLM_TIMEOUT", 120)
    
    schema_desc = _format_schema_for_prompt(schema)
    
    system_prompt = SQL_GENERATION_PROMPT.format(
        schema_description=schema_desc,
        db_type=schema["db_type"]
    )
    
    user_message = {
        "question": question,
        "database": schema["database"]
    }
    
    logger.info(f"Generating SQL for: {question[:60]}...")
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    resp = requests.post(
        f"{api_base}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_message)}
            ],
            "temperature": 0.0
        },
        timeout=timeout
    )
    resp.raise_for_status()
    
    content = resp.json()["choices"][0]["message"]["content"]
    
    # Extract JSON
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse SQL generation response: {content[:200]}")
    
    logger.info(f"SQL generated: confidence={result.get('confidence', 0)}")
    return result


# ============================================================================
# SQL Validation
# ============================================================================

DISALLOWED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "SP_", "XP_", "SCRIPT"
]

ALLOWED_FUNCTIONS = [
    "SUM", "AVG", "COUNT", "MAX", "MIN", "ROUND", "UPPER", "LOWER",
    "DATE_TRUNC", "EXTRACT", "ABS", "CEIL", "FLOOR", "COALESCE", "NULLIF",
    "LENGTH", "TRIM", "SUBSTRING", "CONCAT", "CAST", "TO_CHAR", "TO_DATE"
]


def validate_sql(sql: str, schema: dict) -> dict:
    """Validate SQL for safety.
    
    Args:
        sql: SQL query string
        schema: Database schema
    
    Returns:
        Dict with valid (bool), errors (list)
    """
    errors = []
    sql_upper = sql.upper()
    
    # Check for disallowed keywords
    for keyword in DISALLOWED_KEYWORDS:
        if keyword in sql_upper:
            errors.append(f"Disallowed keyword: {keyword}")
    
    # Must start with SELECT
    if not sql.strip().upper().startswith("SELECT"):
        errors.append("Query must start with SELECT")
    
    # Check for LIMIT
    if "LIMIT" not in sql_upper:
        errors.append("Query should include LIMIT clause")
    
    # Check table names exist
    table_names = [t["name"].upper() for t in schema["tables"]]
    # Simple check - could be improved with SQL parsing
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ============================================================================
# Query Execution
# ============================================================================

def execute_query(sql: str, database: str = None, max_rows: int = 10000) -> dict:
    """Execute SQL query and return results.
    
    Args:
        sql: SQL query
        database: Database name
        max_rows: Maximum rows to return
    
    Returns:
        Dict with columns, rows, row_count, execution_time_ms
    """
    conn, db_type = get_db_connection(database)
    
    try:
        cursor = conn.cursor()
        start_time = datetime.now()
        
        # Add LIMIT if not present
        sql_upper = sql.upper()
        if "LIMIT" not in sql_upper:
            sql = sql.rstrip(";") + f" LIMIT {max_rows}"
        
        cursor.execute(sql)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Get column names
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
        else:
            columns = []
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Convert to dicts
        result_rows = []
        for row in rows[:max_rows]:
            if hasattr(row, 'keys'):
                result_rows.append(dict(row))
            else:
                result_rows.append(dict(zip(columns, row)))
        
        cursor.close()
        
        return {
            "columns": columns,
            "rows": result_rows,
            "row_count": len(result_rows),
            "execution_time_ms": round(execution_time, 2)
        }
    
    finally:
        conn.close()


# ============================================================================
# Results Summarization
# ============================================================================

SUMMARIZATION_PROMPT = """You are a data analyst. Summarize query results for a user.

Original Question: {question}
SQL Query: {sql}
Row Count: {row_count}

Results (first 20 rows):
{results_sample}

Your job:
1. Generate a 1-2 sentence summary answering the original question
2. Extract 2-5 key findings or insights
3. Note any data quality issues

Output format: ONLY valid JSON with keys:
  - summary: string (concise answer)
  - key_findings: list[string] (important insights)
  - data_quality_notes: list[string] (optional issues)

IMPORTANT: Return ONLY the JSON object, no additional text."""


def summarize_results(question: str, sql: str, results: dict) -> dict:
    """Summarize query results using LLM.
    
    Args:
        question: Original question
        sql: Executed SQL
        results: Results dict from execute_query()
    
    Returns:
        Dict with summary, key_findings, data_quality_notes
    """
    api_base = get_env("LLM_API_BASE", required=True)
    model = get_env("LLM_MODEL", required=True)
    api_key = get_env("LLM_API_KEY", "")
    timeout = get_env_int("LLM_TIMEOUT", 60)
    
    # Sample results for LLM
    sample = json.dumps(results["rows"][:20], indent=2)
    
    system_prompt = SUMMARIZATION_PROMPT.format(
        question=question,
        sql=sql,
        row_count=results["row_count"],
        results_sample=sample
    )
    
    logger.info("Summarizing results...")
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    resp = requests.post(
        f"{api_base}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Summarize these results"}
            ],
            "temperature": 0.0
        },
        timeout=timeout
    )
    resp.raise_for_status()
    
    content = resp.json()["choices"][0]["message"]["content"]
    
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            result = {
                "summary": "Query executed successfully",
                "key_findings": [],
                "data_quality_notes": []
            }
    
    return result


# ============================================================================
# XML Export and Storage
# ============================================================================

def results_to_xml(question: str, sql: str, results: dict, summary: dict) -> str:
    """Convert results to XML format.
    
    Args:
        question: Original question
        sql: Executed SQL
        results: Results dict
        summary: Summary dict
    
    Returns:
        XML string
    """
    root = ET.Element("queryResult")
    
    # Metadata
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "query").text = question
    ET.SubElement(metadata, "sql").text = sql
    ET.SubElement(metadata, "generatedAt").text = datetime.utcnow().isoformat() + "Z"
    ET.SubElement(metadata, "rowCount").text = str(results["row_count"])
    ET.SubElement(metadata, "executionTimeMs").text = str(results["execution_time_ms"])
    
    if summary.get("summary"):
        ET.SubElement(metadata, "summary").text = summary["summary"]
    
    # Key findings
    if summary.get("key_findings"):
        findings = ET.SubElement(metadata, "keyFindings")
        for finding in summary["key_findings"]:
            ET.SubElement(findings, "finding").text = finding
    
    # Data quality
    if summary.get("data_quality_notes"):
        quality = ET.SubElement(metadata, "dataQualityNotes")
        for note in summary["data_quality_notes"]:
            ET.SubElement(quality, "note").text = note
    
    # Schema
    schema_elem = ET.SubElement(root, "schema")
    for col in results["columns"]:
        col_elem = ET.SubElement(schema_elem, "column")
        col_elem.set("name", col)
        col_elem.set("type", "string")  # Could be improved with type detection
    
    # Rows
    rows_elem = ET.SubElement(root, "rows")
    for row in results["rows"]:
        row_elem = ET.SubElement(rows_elem, "row")
        for col in results["columns"]:
            val = row.get(col, "")
            # XML doesn't like None
            if val is None:
                val = ""
            ET.SubElement(row_elem, col).text = str(val)
    
    # Pretty print
    xml_str = ET.tostring(root, encoding="unicode")
    return xml_str


def save_to_storage(xml_content: str, filename: str = None) -> dict:
    """Save XML to configured storage.
    
    Args:
        xml_content: XML string
        filename: Optional filename (auto-generated if not provided)
    
    Returns:
        Dict with path, url, storage_type
    """
    storage_type = get_env("STORAGE_TYPE", "local")
    prefix = get_env("STORAGE_PATH_PREFIX", "query_results")
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}/result_{timestamp}.xml"
    
    if storage_type == "local":
        return _save_local(xml_content, filename)
    elif storage_type == "gdrive":
        return _save_gdrive(xml_content, filename)
    elif storage_type == "s3":
        return _save_s3(xml_content, filename)
    elif storage_type == "azure":
        return _save_azure(xml_content, filename)
    elif storage_type == "gcs":
        return _save_gcs(xml_content, filename)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")


def _save_local(xml_content: str, filename: str) -> dict:
    """Save to local filesystem."""
    base_path = get_env("STORAGE_LOCAL_PATH", "./results")
    filepath = Path(base_path) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(xml_content, encoding="utf-8")
    
    return {
        "path": str(filepath),
        "url": f"file://{filepath.absolute()}",
        "storage_type": "local"
    }


def _save_gdrive(xml_content: str, filename: str) -> dict:
    """Save to Google Drive."""
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    
    creds_path = get_env("STORAGE_GDRIVE_CREDENTIALS", required=True)
    folder_id = get_env("STORAGE_GDRIVE_FOLDER_ID")
    
    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
        tmp.write(xml_content)
        tmp_path = tmp.name
    
    try:
        file_metadata = {
            "name": Path(filename).name,
            "mimeType": "application/xml"
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]
        
        media = service.files().create(
            body=file_metadata,
            media_body=tmp_path,
            fields="id, webViewLink"
        ).execute()
        
        return {
            "path": f"gdrive://{file_metadata['name']}",
            "url": media.get("webViewLink", f"gdrive://{media['id']}"),
            "storage_type": "gdrive",
            "file_id": media["id"]
        }
    finally:
        Path(tmp_path).unlink()


def _save_s3(xml_content: str, filename: str) -> dict:
    """Save to S3."""
    import boto3
    
    bucket = get_env("STORAGE_S3_BUCKET", required=True)
    region = get_env("STORAGE_S3_REGION", "us-east-1")
    key = filename
    
    s3 = boto3.client("s3", region_name=region)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=xml_content.encode("utf-8"),
        ContentType="application/xml"
    )
    
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return {
        "path": f"s3://{bucket}/{key}",
        "url": url,
        "storage_type": "s3"
    }


def _save_azure(xml_content: str, filename: str) -> dict:
    """Save to Azure Blob Storage."""
    from azure.storage.blob import BlobServiceClient
    
    conn_str = get_env("STORAGE_AZURE_CONNECTION_STRING", required=True)
    container = get_env("STORAGE_AZURE_CONTAINER", required=True)
    
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service.get_blob_client(container=container, blob=filename)
    blob_client.upload_blob(xml_content.encode("utf-8"), overwrite=True)
    
    return {
        "path": f"azure://{container}/{filename}",
        "url": blob_client.url,
        "storage_type": "azure"
    }


def _save_gcs(xml_content: str, filename: str) -> dict:
    """Save to Google Cloud Storage."""
    from google.cloud import storage
    
    bucket_name = get_env("STORAGE_GCS_BUCKET", required=True)
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(xml_content, content_type="application/xml")
    
    return {
        "path": f"gs://{bucket_name}/{filename}",
        "url": blob.public_url,
        "storage_type": "gcs"
    }


# ============================================================================
# Main Query Function
# ============================================================================

def query(
    question: str,
    database: str = None,
    table_filter: list = None,
    storage_path: str = None
) -> dict:
    """Execute a natural language query and export results as XML.
    
    Args:
        question: Natural language question
        database: Database name (optional)
        table_filter: List of table names to use (optional)
        storage_path: Custom storage path (optional)
    
    Returns:
        Dict with sql, row_count, xml_path, xml_url, summary, key_findings
    """
    start_time = datetime.now()
    
    # Step 1: Discover schema
    logger.info("Discovering schema...")
    schema = discover_schema(database, table_filter)
    
    if not schema["tables"]:
        raise ValueError("No tables found in database")
    
    logger.info(f"Found {len(schema['tables'])} tables")
    
    # Step 2: Generate SQL
    sql_result = generate_sql(question, schema)
    
    if sql_result.get("error") or not sql_result.get("sql"):
        return {
            "success": False,
            "error": sql_result.get("error", "Failed to generate SQL"),
            "reasoning": sql_result.get("reasoning", ""),
            "confidence": sql_result.get("confidence", 0)
        }
    
    sql = sql_result["sql"]
    logger.info(f"Generated SQL: {sql[:100]}...")
    
    # Step 3: Validate SQL
    validation = validate_sql(sql, schema)
    if not validation["valid"]:
        return {
            "success": False,
            "error": f"SQL validation failed: {'; '.join(validation['errors'])}",
            "sql": sql
        }
    
    # Step 4: Execute query
    logger.info("Executing query...")
    results = execute_query(sql, database)
    logger.info(f"Query returned {results['row_count']} rows in {results['execution_time_ms']}ms")
    
    # Step 5: Summarize
    logger.info("Summarizing results...")
    summary = summarize_results(question, sql, results)
    
    # Step 6: Export to XML
    logger.info("Exporting to XML...")
    xml_content = results_to_xml(question, sql, results, summary)
    
    # Generate filename
    if storage_path:
        filename = f"{storage_path}.xml"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', question[:30])
        filename = f"{safe_name}_{timestamp}.xml"
    
    storage_result = save_to_storage(xml_content, filename)
    
    duration = (datetime.now() - start_time).total_seconds()
    
    return {
        "success": True,
        "sql": sql,
        "row_count": results["row_count"],
        "columns": results["columns"],
        "xml_path": storage_result["path"],
        "xml_url": storage_result["url"],
        "storage_type": storage_result["storage_type"],
        "summary": summary.get("summary", ""),
        "key_findings": summary.get("key_findings", []),
        "data_quality_notes": summary.get("data_quality_notes", []),
        "confidence": sql_result.get("confidence", 0),
        "reasoning": sql_result.get("reasoning", ""),
        "execution_time_seconds": round(duration, 2)
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python query_agent.py 'Your natural language question'")
        print("\nEnvironment:")
        print("  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD - Database connection")
        print("  DB_SSL_MODE - SSL mode for secure connections")
        print("  LLM_API_BASE, LLM_MODEL, LLM_API_KEY - LLM configuration")
        print("  STORAGE_TYPE - gdrive, s3, azure, gcs, local")
        print("  STORAGE_* - Storage-specific settings")
        sys.exit(1)
    
    question = sys.argv[1]
    database = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = query(question, database)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
