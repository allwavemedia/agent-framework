-- Migration: Add Context Provider and Memory Models
-- Tasks 4-6 Implementation
-- Date: 2025-01-XX

-- Create conversation_memories table for context provider storage
CREATE TABLE IF NOT EXISTS conversation_memories (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) NOT NULL,
    agent_id INTEGER,
    user_id VARCHAR(255),
    memory_key VARCHAR(255) NOT NULL,
    memory_value JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Create indexes for efficient memory retrieval
CREATE INDEX IF NOT EXISTS idx_conversation_memories_thread_id ON conversation_memories(thread_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memories_agent_id ON conversation_memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memories_user_id ON conversation_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memories_memory_key ON conversation_memories(memory_key);
CREATE INDEX IF NOT EXISTS idx_conversation_memories_created_at ON conversation_memories(created_at);

-- Create context_provider_configs table
CREATE TABLE IF NOT EXISTS context_provider_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    provider_type VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Create index for context provider lookups
CREATE INDEX IF NOT EXISTS idx_context_provider_configs_name ON context_provider_configs(name);
CREATE INDEX IF NOT EXISTS idx_context_provider_configs_provider_type ON context_provider_configs(provider_type);
CREATE INDEX IF NOT EXISTS idx_context_provider_configs_is_active ON context_provider_configs(is_active);

-- Add comments for documentation
COMMENT ON TABLE conversation_memories IS 'Stores conversation history and context for Agent Framework context providers';
COMMENT ON TABLE context_provider_configs IS 'Configuration for context provider instances';

COMMENT ON COLUMN conversation_memories.thread_id IS 'Thread identifier for conversation scoping';
COMMENT ON COLUMN conversation_memories.agent_id IS 'Optional agent association';
COMMENT ON COLUMN conversation_memories.user_id IS 'Optional user association';
COMMENT ON COLUMN conversation_memories.memory_key IS 'Memory category or key';
COMMENT ON COLUMN conversation_memories.memory_value IS 'JSON storage for memory content';

COMMENT ON COLUMN context_provider_configs.name IS 'Unique name for the context provider';
COMMENT ON COLUMN context_provider_configs.provider_type IS 'Type of provider (simple, mem0, redis, custom)';
COMMENT ON COLUMN context_provider_configs.config IS 'JSON configuration for the provider';
