#!/usr/bin/env python3
"""Example: Agent using the query-agent skill."""

import os
from query_agent import query, discover_schema


def example_basic_query():
    """Example: Basic natural language query with local storage."""
    print("=" * 60)
    print("Example 1: Basic Query with Local Storage")
    print("=" * 60)
    
    # Database connection
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_HOST"] = "db.example.com"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "user"
    os.environ["DB_PASSWORD"] = "password"
    os.environ["DB_NAME"] = "analytics"
    os.environ["DB_SSL_MODE"] = "require"
    
    # LLM (OpenAI)
    os.environ["LLM_API_BASE"] = "https://api.openai.com/v1"
    os.environ["LLM_MODEL"] = "gpt-4"
    os.environ["LLM_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    # Storage: Local
    os.environ["STORAGE_TYPE"] = "local"
    os.environ["STORAGE_LOCAL_PATH"] = "./results"
    
    # Query
    # result = query("What were total sales by month in 2023?")
    # print(f"SQL: {result['sql']}")
    # print(f"Rows: {result['row_count']}")
    # print(f"XML: {result['xml_path']}")
    # print(f"Summary: {result['summary']}")
    
    print("(Uncomment to run with real credentials)")


def example_gdrive_export():
    """Example: Export results to Google Drive."""
    print("\n" + "=" * 60)
    print("Example 2: Export to Google Drive")
    print("=" * 60)
    
    os.environ["DB_HOST"] = "mydb.postgres.database.azure.com"
    os.environ["DB_USER"] = "admin@mydb"
    os.environ["DB_PASSWORD"] = "secret"
    os.environ["DB_SSL_MODE"] = "require"
    os.environ["DB_NAME"] = "production"
    
    os.environ["LLM_API_BASE"] = "https://api.openai.com/v1"
    os.environ["LLM_MODEL"] = "gpt-4"
    os.environ["LLM_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    # Google Drive storage
    os.environ["STORAGE_TYPE"] = "gdrive"
    os.environ["STORAGE_GDRIVE_CREDENTIALS"] = "./gdrive-service-account.json"
    os.environ["STORAGE_GDRIVE_FOLDER_ID"] = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
    
    # result = query(
    #     question="Top 10 customers by revenue",
    #     storage_path="reports/top_customers"
    # )
    # print(f"Google Drive URL: {result['xml_url']}")
    
    print("(Uncomment to run)")


def example_s3_export():
    """Example: Export results to S3."""
    print("\n" + "=" * 60)
    print("Example 3: Export to S3")
    print("=" * 60)
    
    os.environ["DB_HOST"] = "mydb.abc123.us-east-1.rds.amazonaws.com"
    os.environ["DB_USER"] = "admin"
    os.environ["DB_PASSWORD"] = "secret"
    os.environ["DB_SSL_MODE"] = "require"
    os.environ["DB_SSL_ROOT_CERT"] = "./rds-ca-cert.pem"
    
    os.environ["LLM_API_BASE"] = "https://api.openai.com/v1"
    os.environ["LLM_MODEL"] = "gpt-4"
    os.environ["LLM_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    # S3 storage
    os.environ["STORAGE_TYPE"] = "s3"
    os.environ["STORAGE_S3_BUCKET"] = "my-query-results"
    os.environ["STORAGE_S3_PREFIX"] = "analytics"
    os.environ["STORAGE_S3_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    # result = query("Monthly growth rate by region")
    # print(f"S3 URL: {result['xml_url']}")
    
    print("(Uncomment to run)")


def example_multi_table():
    """Example: Query across multiple tables with hints."""
    print("\n" + "=" * 60)
    print("Example 4: Multi-Table Query with Hints")
    print("=" * 60)
    
    os.environ["DB_HOST"] = "warehouse.example.com"
    os.environ["DB_USER"] = "analyst"
    os.environ["DB_PASSWORD"] = "password"
    os.environ["DB_NAME"] = "warehouse"
    os.environ["DB_SSL_MODE"] = "require"
    
    os.environ["LLM_API_BASE"] = "http://localhost:11434/v1"
    os.environ["LLM_MODEL"] = "qwen2.5-coder:14b"
    
    os.environ["STORAGE_TYPE"] = "local"
    os.environ["STORAGE_LOCAL_PATH"] = "./results"
    
    # Provide table hints to help SQL generation
    # result = query(
    #     question="What products had the highest return rates?",
    #     table_filter=["orders", "products", "returns"],
    #     storage_path="reports/return_analysis"
    # )
    # print(f"Found {result['row_count']} products")
    # print(f"Key findings: {result['key_findings']}")
    
    print("(Uncomment to run)")


def example_schema_discovery():
    """Example: Discover database schema."""
    print("\n" + "=" * 60)
    print("Example 5: Schema Discovery")
    print("=" * 60)
    
    os.environ["DB_TYPE"] = "postgresql"
    os.environ["DB_HOST"] = "db.example.com"
    os.environ["DB_USER"] = "user"
    os.environ["DB_PASSWORD"] = "pass"
    os.environ["DB_NAME"] = "production"
    
    # Discover all tables
    # schema = discover_schema()
    # print(f"Database: {schema['database']}")
    # print(f"Tables: {len(schema['tables'])}")
    # for table in schema['tables']:
    #     print(f"  - {table['name']}: {len(table['columns'])} columns")
    
    # Discover specific tables only
    # schema = discover_schema(table_filter=["sales", "customers"])
    
    print("(Uncomment to run)")


def example_batch_queries():
    """Example: Run multiple queries."""
    print("\n" + "=" * 60)
    print("Example 6: Batch Queries")
    print("=" * 60)
    
    os.environ["DB_HOST"] = "analytics.example.com"
    os.environ["DB_USER"] = "analyst"
    os.environ["DB_PASSWORD"] = "secret"
    os.environ["DB_NAME"] = "analytics"
    os.environ["DB_SSL_MODE"] = "require"
    
    os.environ["LLM_API_BASE"] = "https://api.openai.com/v1"
    os.environ["LLM_MODEL"] = "gpt-4"
    os.environ["LLM_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    os.environ["STORAGE_TYPE"] = "gdrive"
    os.environ["STORAGE_GDRIVE_CREDENTIALS"] = "./gdrive-credentials.json"
    
    questions = [
        "Total revenue by quarter",
        "Top 10 products by units sold",
        "Customer acquisition by channel",
        "Average order value trend",
    ]
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\nQuery {i}: {question}")
        # result = query(
        #     question=question,
        #     storage_path=f"reports/daily_report_{i}"
        # )
        # results.append(result)
        # print(f"  ✓ {result['row_count']} rows")
        # print(f"  ✓ {result['summary'][:60]}...")
    
    print("\n(No queries configured - uncomment to run)")
    
    if results:
        print(f"\nCompleted {len(results)} queries")


def example_sqlite_local():
    """Example: Use local SQLite database."""
    print("\n" + "=" * 60)
    print("Example 7: SQLite Local Database")
    print("=" * 60)
    
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["DB_NAME"] = "./my_data.db"
    
    os.environ["LLM_API_BASE"] = "http://localhost:11434/v1"
    os.environ["LLM_MODEL"] = "qwen2.5-coder:14b"
    
    os.environ["STORAGE_TYPE"] = "local"
    os.environ["STORAGE_LOCAL_PATH"] = "./results"
    
    # result = query("Show me all records from last week")
    # print(f"Results saved to: {result['xml_path']}")
    
    print("(Uncomment to run)")


def main():
    """Run all examples."""
    example_basic_query()
    example_gdrive_export()
    example_s3_export()
    example_multi_table()
    example_schema_discovery()
    example_batch_queries()
    example_sqlite_local()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
Key Features Demonstrated:
1. Basic natural language to SQL
2. Export to Google Drive
3. Export to S3 with SSL certs
4. Multi-table queries with hints
5. Schema discovery
6. Batch query execution
7. Local SQLite support

All configuration via environment variables!
""")


if __name__ == "__main__":
    main()
