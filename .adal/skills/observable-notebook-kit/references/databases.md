# Database Connectors Reference

## Configuration File

Configure databases in `.observable/databases.json`:

```json
{
  "my-db": {
    "type": "duckdb",
    "path": "./data.duckdb"
  }
}
```

## DuckDB

```ts
type DuckDBConfig = {
  type: "duckdb";
  path?: string;  // default: ":memory:"
  options?: {[key: string]: string};
}
```

Query Parquet/CSV directly:
```sql
SELECT * FROM read_parquet('file.parquet')
SELECT * FROM read_csv('file.csv')
```

## SQLite

```ts
type SQLiteConfig = {
  type: "sqlite";
  path?: string;  // default: ":memory:"
}
```

Requires Node.js 24+ (uses `node:sqlite`).

## Postgres

```ts
type PostgresConfig = {
  type: "postgres";
  host?: string;
  port?: string | number;
  username?: string;
  password?: string;
  database?: string;
  ssl?: boolean;
}
```

Default: localhost with default user. Works with Postgres-compatible DBs (ClickHouse, Redshift, Cloud SQL).

## Snowflake

```ts
type SnowflakeConfig = {
  type: "snowflake";
  account: string;
  database?: string;
  role?: string;
  schema?: string;
  username?: string;
  warehouse?: string;
  password?: string;
}
```

## BigQuery

```ts
type BigQueryConfig = {
  type: "bigquery";
  apiKey?: string;
  keyFilename?: string;
  keyFile?: string;
  projectId?: string;
}
```

Uses Google Cloud SDK authentication.

## Databricks

```ts
type DatabricksConfig = {
  type: "databricks";
  host: string;
  path: string;
} & (
  | {authType?: "access-token"; token: string}
  | {authType: "databricks-oauth"; oauthClientId?: string; oauthClientSecret?: string}
)
```

## SQL Cell Usage

Basic:
```html
<script type="application/sql" output="results">
  SELECT * FROM table
</script>
```

With database:
```html
<script type="application/sql" database="my-db" output="data">
  SELECT * FROM customers WHERE active = true
</script>
```

Hidden (no table display):
```html
<script type="application/sql" database="my-db" output="data" hidden>
  SELECT * FROM large_table
</script>
```

## Dynamic Queries (JavaScript)

```js
const db = DatabaseClient("duckdb");
const rows = await db.sql`SELECT * FROM t WHERE id = ${id}`;
```

Note: Dynamic queries only work in Desktop or preview mode, not in built static sites.

## Client-Side Databases

Use `var:` prefix for browser-side databases:

```html
<script type="application/sql" database="var:db" output="results">
  SELECT * FROM data
</script>
```

Provide matching client:
```js
const db = await DuckDBClient.of({data: FileAttachment("data.parquet")});
```

## Cache Management

Results stored in `.observable/cache/`. To refresh:
- Desktop: Click Play or Shift+Enter
- Notebook Kit: Delete cache file, or use CI/CD

## Security

- Connectors run locally (data stays private)
- Keep `databases.json` out of git (contains credentials)
- Use folder isolation for different trust levels
