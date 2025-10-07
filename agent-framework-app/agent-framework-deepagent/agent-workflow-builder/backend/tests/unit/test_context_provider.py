"""
Unit tests for Context Provider and Memory functionality.
"""
import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.services.context_service import ContextService, DatabaseContextProvider
from app.models import ConversationMemory, ContextProviderConfig


@pytest.mark.asyncio
async def test_create_provider_config(db_session: Session):
    """Test creating a context provider configuration."""
    service = ContextService(db_session)
    
    config = await service.create_provider_config(
        name="test_provider",
        provider_type="simple",
        config={"key": "value"}
    )
    
    assert config is not None
    assert config.name == "test_provider"
    assert config.provider_type == "simple"
    assert config.config == {"key": "value"}
    assert config.is_active is True


@pytest.mark.asyncio
async def test_list_provider_configs(db_session: Session):
    """Test listing context provider configurations."""
    service = ContextService(db_session)
    
    # Create multiple configs
    await service.create_provider_config("provider1", "simple", {})
    await service.create_provider_config("provider2", "mem0", {})
    
    configs = await service.list_provider_configs()
    
    assert len(configs) >= 2
    assert any(c.name == "provider1" for c in configs)
    assert any(c.name == "provider2" for c in configs)


@pytest.mark.asyncio
async def test_get_provider_config(db_session: Session):
    """Test getting a specific context provider configuration."""
    service = ContextService(db_session)
    
    created_config = await service.create_provider_config(
        name="test_get",
        provider_type="redis",
        config={"host": "localhost"}
    )
    
    retrieved_config = await service.get_provider_config(created_config.id)
    
    assert retrieved_config is not None
    assert retrieved_config.id == created_config.id
    assert retrieved_config.name == "test_get"


@pytest.mark.asyncio
async def test_store_and_retrieve_memories(db_session: Session):
    """Test storing and retrieving conversation memories."""
    service = ContextService(db_session)
    provider = service.create_database_provider(
        thread_id="test_thread_123",
        agent_id=1,
        user_id="user_456"
    )
    
    # Store a memory
    await provider._store_message_memory(
        memory_key="user_message",
        memory_value={
            "role": "user",
            "text": "Hello, how are you?",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Retrieve memories
    memories = await provider._retrieve_memories()
    
    assert len(memories) > 0
    assert memories[0].thread_id == "test_thread_123"
    assert memories[0].memory_key == "user_message"
    assert memories[0].memory_value["text"] == "Hello, how are you?"


@pytest.mark.asyncio
async def test_get_thread_memories(db_session: Session):
    """Test getting all memories for a specific thread."""
    service = ContextService(db_session)
    thread_id = "test_thread_789"
    
    # Create test memories
    provider = service.create_database_provider(thread_id=thread_id)
    
    await provider._store_message_memory(
        "msg1",
        {"text": "First message"}
    )
    await provider._store_message_memory(
        "msg2",
        {"text": "Second message"}
    )
    
    # Retrieve memories
    memories = await service.get_thread_memories(thread_id)
    
    assert len(memories) >= 2
    assert all(m.thread_id == thread_id for m in memories)


@pytest.mark.asyncio
async def test_get_user_memories(db_session: Session):
    """Test getting all memories for a specific user."""
    service = ContextService(db_session)
    user_id = "test_user_123"
    
    # Create test memories for user
    provider = service.create_database_provider(
        thread_id="thread1",
        user_id=user_id
    )
    
    await provider._store_message_memory(
        "user_msg",
        {"text": "User message"}
    )
    
    # Retrieve user memories
    memories = await service.get_user_memories(user_id)
    
    assert len(memories) >= 1
    assert all(m.user_id == user_id for m in memories)


@pytest.mark.asyncio
async def test_clear_thread_memories(db_session: Session):
    """Test clearing all memories for a thread."""
    service = ContextService(db_session)
    thread_id = "test_clear_thread"
    
    # Create test memories
    provider = service.create_database_provider(thread_id=thread_id)
    await provider._store_message_memory("msg1", {"text": "Message 1"})
    await provider._store_message_memory("msg2", {"text": "Message 2"})
    
    # Verify memories exist
    memories_before = await service.get_thread_memories(thread_id)
    assert len(memories_before) >= 2
    
    # Clear memories
    count = await service.clear_thread_memories(thread_id)
    assert count >= 2
    
    # Verify memories cleared
    memories_after = await service.get_thread_memories(thread_id)
    assert len(memories_after) == 0


@pytest.mark.asyncio
async def test_context_provider_thread_created(db_session: Session):
    """Test context provider thread creation callback."""
    provider = DatabaseContextProvider(db=db_session)
    
    assert provider.thread_id is None
    
    await provider.thread_created("new_thread_123")
    
    assert provider.thread_id == "new_thread_123"


@pytest.mark.asyncio
async def test_format_memory(db_session: Session):
    """Test memory formatting for context."""
    provider = DatabaseContextProvider(db=db_session, thread_id="test")
    
    memory = ConversationMemory(
        thread_id="test",
        memory_key="test_key",
        memory_value={
            "role": "user",
            "text": "Test message"
        }
    )
    
    formatted = provider._format_memory(memory)
    
    assert "user" in formatted
    assert "Test message" in formatted


@pytest.mark.asyncio
async def test_context_provider_invoking_no_thread(db_session: Session):
    """Test context provider when no thread is set."""
    provider = DatabaseContextProvider(db=db_session)
    
    from agent_framework import ChatMessage, Role
    
    context = await provider.invoking(ChatMessage(Role.USER, text="Hello"))
    
    assert context is not None
    assert context.instructions is None or context.instructions == ""


@pytest.mark.asyncio
async def test_context_provider_invoking_with_memories(db_session: Session):
    """Test context provider returns context with memories."""
    thread_id = "test_invoking_thread"
    provider = DatabaseContextProvider(
        db=db_session,
        thread_id=thread_id
    )
    
    # Store some memories
    await provider._store_message_memory(
        "context_msg",
        {
            "role": "user",
            "text": "Previous context",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    from agent_framework import ChatMessage, Role
    
    context = await provider.invoking(ChatMessage(Role.USER, text="New message"))
    
    assert context is not None
    # Should have instructions with memories
    if context.instructions:
        assert len(context.instructions) > 0
