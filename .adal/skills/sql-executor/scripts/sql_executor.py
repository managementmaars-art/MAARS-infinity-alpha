#!/usr/bin/env python3
"""
SQL Executor Tool - Execute SQL queries against databases.
Based on Python's sqlite3: https://github.com/python/cpython

Usage:
    python sql_executor.py database.db "SELECT * FROM users"
    python sql_executor.py database.db "SELECT * FROM orders" --output orders.csv
    python sql_executor.py database.db --file queries.sql
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

def execute_query(db_path, query, output=None, format='table'):
    """Execute SQL query and display/export results."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            if not rows:
                print("No results found.")
                return
            
            columns = [desc[0] for desc in cursor.description]
            data = [dict(row) for row in rows]
            
            if output:
                ext = Path(output).suffix.lower()
                if ext == '.csv':
                    with open(output, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=columns)
                        writer.writeheader()
                        writer.writerows(data)
                elif ext == '.json':
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Exported {len(data)} rows to {output}")
            else:
                # Print as table
                print(' | '.join(columns))
                print('-' * 60)
                for row in data[:50]:
                    print(' | '.join(str(row.get(c, ''))[:20] for c in columns))
                if len(data) > 50:
                    print(f"... and {len(data) - 50} more rows")
                print(f"\n✓ {len(data)} rows returned")
        else:
            conn.commit()
            print(f"✓ Query executed. Rows affected: {cursor.rowcount}")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Execute SQL queries")
    parser.add_argument('database', help='SQLite database file')
    parser.add_argument('query', nargs='?', help='SQL query to execute')
    parser.add_argument('--file', '-f', help='SQL file to execute')
    parser.add_argument('--output', '-o', help='Output file (csv/json)')
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, 'r') as f:
            query = f.read()
    elif args.query:
        query = args.query
    else:
        parser.error("Provide a query or --file")
    
    execute_query(args.database, query, args.output)

if __name__ == "__main__":
    main()
