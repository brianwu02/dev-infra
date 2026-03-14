---
name: db-schema
description: Database schema reference for the hello-world app's TimescaleDB instance. Use when writing queries, creating migrations, or debugging data issues.
user-invokable: false
---

# Database Schema Reference

**Engine**: TimescaleDB (Postgres + TimescaleDB extension)
**Connection**: `timescaledb:5432/devdb` (from within Docker network)
**User**: `devuser` / `changeme`

## Tables

### hello_counter
Single-row counter table for the hit counter.

| Column | Type | Notes |
|--------|------|-------|
| id | integer | PK, always 1 (CHECK constraint) |
| hits | bigint | Current hit count, default 0 |

Auto-created on app startup via the FastAPI lifespan handler.

## Common Query Patterns

```sql
-- Read current count
SELECT hits FROM hello_counter WHERE id = 1;

-- Increment
UPDATE hello_counter SET hits = hits + 1 WHERE id = 1 RETURNING hits;

-- Reset
UPDATE hello_counter SET hits = 0 WHERE id = 1;
```

## Extending the Schema

When adding new tables, follow these patterns:

### Regular Tables
```sql
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Time-Series Tables (Hypertables)
```sql
CREATE TABLE IF NOT EXISTS events (
    time TIMESTAMPTZ NOT NULL,
    name TEXT NOT NULL,
    payload JSONB DEFAULT '{}'
);
SELECT create_hypertable('events', 'time', if_not_exists => TRUE);
```

### Indexing Guidelines
- Always index foreign keys
- Use GIN indexes for JSONB columns
- Hypertable indexes should include the time column for partition pruning
- Check existing indexes: `\di+ tablename`

## asyncpg Query Conventions

```python
# Parameterized queries — ALWAYS use $N placeholders
row = await pool.fetchrow("SELECT hits FROM hello_counter WHERE id = $1", 1)

# NEVER interpolate values into SQL
# BAD: f"SELECT * FROM items WHERE id = {user_input}"

# Fetch multiple rows
rows = await pool.fetch("SELECT * FROM items ORDER BY created_at DESC LIMIT $1", limit)

# Execute without return
await pool.execute("UPDATE hello_counter SET hits = 0 WHERE id = 1")

# Fetch with RETURNING
row = await pool.fetchrow(
    "UPDATE hello_counter SET hits = hits + 1 WHERE id = 1 RETURNING hits"
)
```
