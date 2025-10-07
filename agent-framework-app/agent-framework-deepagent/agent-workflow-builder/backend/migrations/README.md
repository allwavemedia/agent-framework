# Database Migrations

## Overview

This directory contains SQL migration scripts for the Agent Workflow Builder database.

## Migrations

### add_context_provider_models.sql

Adds support for Context Providers and Conversation Memory (Tasks 4-6).

**Tables Created:**
- `conversation_memories`: Stores conversation history and context
- `context_provider_configs`: Configuration for context provider instances

**Indexes Created:**
- Efficient lookups by thread_id, user_id, agent_id
- Memory key indexing
- Timestamp indexing for chronological queries

## Running Migrations

### Using psql

```bash
# Connect to your database
psql -U your_user -d agent_workflows

# Run the migration
\i migrations/add_context_provider_models.sql
```

### Using SQLModel/Alembic (if configured)

```bash
# Generate migration from models
alembic revision --autogenerate -m "Add context provider models"

# Apply migration
alembic upgrade head
```

### Manual SQL Execution

```sql
-- Copy and paste the contents of add_context_provider_models.sql
-- into your SQL client
```

## Verification

After running migrations, verify tables were created:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('conversation_memories', 'context_provider_configs');

-- Check indexes
SELECT indexname 
FROM pg_indexes 
WHERE tablename IN ('conversation_memories', 'context_provider_configs');
```

## Rollback

To rollback the context provider migrations:

```sql
-- Drop tables (will cascade and remove all data)
DROP TABLE IF EXISTS conversation_memories CASCADE;
DROP TABLE IF EXISTS context_provider_configs CASCADE;
```

**Warning**: This will permanently delete all conversation memory data!
