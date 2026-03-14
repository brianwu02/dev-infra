---
name: db-schema
description: Database schema reference — all tables, columns, relationships, and common query patterns.
user-invokable: false
---

# Database Schema

## Connection

```bash
# From dev-box or host
psql -h localhost -p 5432 -U devuser -d devdb
```

## Core Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| email | TEXT UNIQUE | NOT NULL |
| name | TEXT | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### items
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| name | TEXT | NOT NULL |
| description | TEXT | |
| category | TEXT | |
| user_id | INT FK → users | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | |

### audit_log
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL PK | |
| table_name | TEXT | |
| record_id | INT | |
| action | TEXT | INSERT/UPDATE/DELETE |
| changed_by | INT FK → users | |
| changed_at | TIMESTAMPTZ | DEFAULT NOW() |
| old_data | JSONB | |
| new_data | JSONB | |

## Indexes

```sql
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
```

## Common Query Patterns

```sql
-- List with pagination
SELECT * FROM items ORDER BY created_at DESC LIMIT $1 OFFSET $2;

-- Full-text search
SELECT * FROM items WHERE name ILIKE '%' || $1 || '%';

-- Join with user
SELECT i.*, u.name as user_name
FROM items i JOIN users u ON i.user_id = u.id
WHERE i.category = $1;

-- Aggregate by category
SELECT category, COUNT(*) as count
FROM items GROUP BY category ORDER BY count DESC;
```

## Migrations

Located in `backend/migrations/`, numbered sequentially.
Run with: `psql -h localhost -p 5432 -U devuser -d devdb -f backend/migrations/NNN_name.sql`
