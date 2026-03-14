---
name: add-migration
description: Create a new database migration file with proper numbering, transaction wrapping, and dependent code updates.
user-invokable: true
argument-hint: "description of the migration"
---

# Add a Database Migration

## Step 1: Create Migration File

Check the latest migration number:
```bash
ls backend/migrations/ | tail -5
```

Create `backend/migrations/{NNN}_descriptive_name.sql`:

```sql
BEGIN;

-- Migration: $ARGUMENTS
-- Created: $(date +%Y-%m-%d)

CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_new_table_name ON new_table(name);

COMMIT;
```

### Conventions
- Sequential numbering: `001`, `002`, ..., `049`, `050`
- File name: `{NNN}_descriptive_name.sql` (snake_case)
- Always wrap in `BEGIN` / `COMMIT`
- Use `IF NOT EXISTS` / `IF EXISTS` for idempotency
- Add indexes for foreign keys and frequently queried columns

## Step 2: Run Migration

```bash
psql -h localhost -p 5432 -U devuser -d devdb -f backend/migrations/{NNN}_descriptive_name.sql
```

## Step 3: Update Dependent Code

1. **Pydantic schema** in `backend/domains/{domain}/schemas.py`
2. **Query functions** in `backend/domains/{domain}/queries.py`
3. **Zod schema** in `frontend/src/api/schemas/{domain}.schema.ts`
4. **TypeScript type** in `frontend/src/api/types.ts`

## Step 4: Verify

```bash
# Confirm table/column exists
psql -h localhost -p 5432 -U devuser -d devdb -c "\d new_table"

# Run tests
cd frontend && npx tsc --noEmit && npx vitest run
cd backend && python -m pytest tests/ -v
```
