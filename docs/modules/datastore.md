# :floppy_disk: Local Datastore

Local SQLite persistence layer for storing agent-generated data, fetched API results, or any structured data. Tables persist across sessions at `~/.mcp-canada/datastore.db`.

> **Note:** `ds_query` supports SELECT, PRAGMA, EXPLAIN, and CREATE INDEX only -- no mutations via query. Use `ds_insert_data` to write data. Table and column names are validated against an allowlist regex to prevent SQL injection.

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (6)

<!-- CATALOG:datastore:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ds_create_table` | Create a named table in the local SQLite datastore. | `table_name`, `columns`, `data` |
| `ds_insert_data` | Insert rows of data into an existing table in the local SQLite datastore. | `table_name`, `rows` |
| `ds_query` | Run a read-only SQL query against the local SQLite datastore. | `sql` |
| `ds_list_tables` | List all tables in the local SQLite datastore. | -- |
| `ds_get_schema` | Get the column schema for a table in the local SQLite datastore. | `table_name` |
| `ds_drop_table` | Drop (delete) a table from the local SQLite datastore. | `table_name` |
<!-- CATALOG:datastore:end -->

## Prompts (4)

| Prompt | Type | Description |
|--------|------|-------------|
| `ds_create_and_query` | Guided | Create a table, insert data, and run SQL queries |
| `ds_quick_query` | Quick | Run a SQL query against an existing datastore table |
| `ds_explore_tables` | Quick | List tables and inspect schemas |
| `ds_cross_module_join` | Guided | Fetch data from two APIs and JOIN in SQL |

## Resources (6)

| URI | Type | Description |
|-----|------|-------------|
| `data://datastore/column-types` | Catalog | Supported SQLite column types with examples |
| `data://datastore/identifier-rules` | Catalog | Identifier regex pattern and allowed characters |
| `docs://datastore/sql-guide` | Guide | Supported SQL statements, query examples, safety rules |
| `docs://datastore/cross-module-patterns` | Guide | Fetch-store-JOIN workflow for cross-API analytics |
| `template://datastore/query-report` | Template | SQL query result report template |
| `template://datastore/schema-report` | Template | Table schema description template |
