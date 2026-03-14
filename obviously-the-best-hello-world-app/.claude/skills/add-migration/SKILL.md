---
name: add-migration
description: Create a new database migration for PostgreSQL. Covers file naming, SQL patterns, running, and updating dependent code.
user-invokable: true
argument-hint: description of the schema change
---

# Add a Database Migration

## 1. Determine Next Migration Number

Check existing migrations:

```bash
ls migrations/ | sort -n | tail -5
```

Use the next sequential number, zero-padded to 3 digits.

## 2. Create Migration File

Create `migrations/{NNN}_$ARGUMENTS.sql`:

```sql
-- Migration: {NNN} $ARGUMENTS
-- Date: $(date +%Y-%m-%d)

BEGIN;

-- Your DDL here
CREATE TABLE IF NOT EXISTS my_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value NUMERIC NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_my_table_name ON my_table(name);

COMMIT;
```

## 3. Migration Best Practices

### Always Use Transactions
Wrap all DDL in `BEGIN/COMMIT` so failures roll back cleanly.

### Idempotent Statements
Use `IF NOT EXISTS` / `IF EXISTS` so migrations can be re-run safely:
```sql
CREATE TABLE IF NOT EXISTS ...
CREATE INDEX IF NOT EXISTS ...
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS new_col TEXT;
DROP INDEX IF EXISTS old_index;
```

### Foreign Keys
Always index foreign key columns:
```sql
ALTER TABLE child_table ADD COLUMN parent_id INTEGER REFERENCES parent_table(id);
CREATE INDEX IF NOT EXISTS idx_child_parent_id ON child_table(parent_id);
```

## 4. Run Migration

```bash
psql "$DATABASE_URL" -f migrations/{NNN}_$ARGUMENTS.sql
```

If DDL requires superuser privileges (creating extensions, altering roles):
```bash
psql "$SUPER_DATABASE_URL" -f migrations/{NNN}_$ARGUMENTS.sql
```

## 5. Update Dependent Code

- Add/update Pydantic response models if new columns are exposed via API
- Add/update query functions to SELECT/INSERT the new columns
- If creating a new table, consider adding a new endpoint (`/add-endpoint`)

## 6. Verify

```bash
# Confirm migration applied
psql "$DATABASE_URL" -c "\d+ my_table"

# Restart app to pick up any schema changes
docker compose restart hello-world

# Run tests
python -m pytest tests/ -v
```
