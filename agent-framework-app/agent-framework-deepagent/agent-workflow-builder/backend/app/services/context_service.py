"""
Context Provider Service for managing conversation memory and context.
Implements Microsoft Agent Framework ContextProvider patterns.
"""
from typing import Dict, Any, Optional, List, Sequence
from datetime import datetime
from sqlmodel import Session, select
from agent_framework import ContextProvider, Context, ChatMessage

from app.models import ConversationMemory, ContextProviderConfig
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseContextProvider(ContextProvider):
    """
    Database-backed context provider for persistent conversation memory.
    
    This implements the Microsoft Agent Framework ContextProvider pattern
    and stores memories in a database for persistence across sessions.
    """
    
    def __init__(
        self,
        db: Session,
        thread_id: Optional[str] = None,
        agent_id: Optional[int] = None,
        user_id: Optional[str] = None,
        context_prompt: str = ContextProvider.DEFAULT_CONTEXT_PROMPT
    ):
        """
        Initialize the database context provider.
        
        Args:
            db: Database session
            thread_id: Thread identifier for scoping memories
            agent_id: Agent identifier for scoping memories
            user_id: User identifier for scoping memories
            context_prompt: Prompt to prepend to retrieved memories
        """
        self.db = db
        self.thread_id = thread_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.context_prompt = context_prompt
    
    async def thread_created(self, thread_id: str | None) -> None:
        """Called when a new thread is created."""
        if thread_id:
            self.thread_id = thread_id
            logger.info(f"Context provider tracking new thread: {thread_id}")
    
    async def invoked(
        self,
        request_messages: ChatMessage | Sequence[ChatMessage],
        response_messages: ChatMessage | Sequence[ChatMessage] | None = None,
        invoke_exception: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Called after agent invocation to store conversation context.
        
        This extracts and stores important information from the conversation.
        """
        if not self.thread_id:
            logger.warning("No thread_id set, skipping memory storage")
            return
        
        try:
            # Store request messages
            if isinstance(request_messages, ChatMessage):
                request_messages = [request_messages]
            
            for msg in request_messages:
                if hasattr(msg, 'role') and hasattr(msg, 'text'):
                    await self._store_message_memory(
                        memory_key=f"message_{msg.role.value}",
                        memory_value={
                            "role": msg.role.value,
                            "text": msg.text,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
            
            # Store response messages if available
            if response_messages:
                if isinstance(response_messages, ChatMessage):
                    response_messages = [response_messages]
                
                for msg in response_messages:
                    if hasattr(msg, 'role') and hasattr(msg, 'text'):
                        await self._store_message_memory(
                            memory_key=f"message_{msg.role.value}_response",
                            memory_value={
                                "role": msg.role.value,
                                "text": msg.text,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
            
            logger.debug(f"Stored conversation memory for thread {self.thread_id}")
            
        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
    
    async def invoking(
        self, 
        messages: ChatMessage | Sequence[ChatMessage], 
        **kwargs: Any
    ) -> Context:
        """
        Called before agent invocation to provide context from memory.
        
        Returns:
            Context object with instructions and relevant memories
        """
        if not self.thread_id:
            return Context()
        
        try:
            # Retrieve relevant memories for this thread
            memories = await self._retrieve_memories()
            
            if not memories:
                return Context()
            
            # Format memories as instructions
            memory_instructions = [self.context_prompt]
            
            for memory in memories:
                memory_text = self._format_memory(memory)
                if memory_text:
                    memory_instructions.append(memory_text)
            
            instructions = "\n".join(memory_instructions)
            
            return Context(instructions=instructions)
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return Context()
    
    async def _store_message_memory(
        self, 
        memory_key: str, 
        memory_value: Dict[str, Any]
    ) -> None:
        """Store a memory entry in the database."""
        try:
            memory = ConversationMemory(
                thread_id=self.thread_id,
                agent_id=self.agent_id,
                user_id=self.user_id,
                memory_key=memory_key,
                memory_value=memory_value,
                created_at=datetime.utcnow()
            )
            
            self.db.add(memory)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            await self.db.rollback()
    
    async def _retrieve_memories(
        self, 
        limit: int = 10
    ) -> List[ConversationMemory]:
        """Retrieve recent memories for the current thread."""
        try:
            query = select(ConversationMemory).where(
                ConversationMemory.thread_id == self.thread_id
            ).order_by(
                ConversationMemory.created_at.desc()
            ).limit(limit)
            
            result = await self.db.execute(query)
            memories = result.scalars().all()
            
            return list(reversed(memories))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    def _format_memory(self, memory: ConversationMemory) -> str:
        """Format a memory entry for inclusion in context."""
        try:
            value = memory.memory_value
            
            if "text" in value:
                role = value.get("role", "unknown")
                text = value.get("text", "")
                return f"- {role}: {text}"
            
            return f"- {memory.memory_key}: {value}"
            
        except Exception as e:
            logger.error(f"Error formatting memory: {e}")
            return ""


class ContextService:
    """Service for managing context providers and conversation memory."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_provider_config(
        self,
        name: str,
        provider_type: str,
        config: Dict[str, Any]
    ) -> ContextProviderConfig:
        """Create a new context provider configuration."""
        try:
            provider_config = ContextProviderConfig(
                name=name,
                provider_type=provider_type,
                config=config,
                created_at=datetime.utcnow()
            )
            
            self.db.add(provider_config)
            await self.db.commit()
            await self.db.refresh(provider_config)
            
            logger.info(f"Created context provider config: {name}")
            return provider_config
            
        except Exception as e:
            logger.error(f"Error creating provider config: {e}")
            await self.db.rollback()
            raise
    
    async def get_provider_config(self, config_id: int) -> Optional[ContextProviderConfig]:
        """Get a context provider configuration by ID."""
        query = select(ContextProviderConfig).where(
            ContextProviderConfig.id == config_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_provider_configs(self) -> List[ContextProviderConfig]:
        """List all context provider configurations."""
        query = select(ContextProviderConfig).where(
            ContextProviderConfig.is_active == True
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_thread_memories(
        self,
        thread_id: str,
        limit: int = 50
    ) -> List[ConversationMemory]:
        """Get conversation memories for a specific thread."""
        query = select(ConversationMemory).where(
            ConversationMemory.thread_id == thread_id
        ).order_by(
            ConversationMemory.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[ConversationMemory]:
        """Get conversation memories for a specific user."""
        query = select(ConversationMemory).where(
            ConversationMemory.user_id == user_id
        ).order_by(
            ConversationMemory.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def clear_thread_memories(self, thread_id: str) -> int:
        """Clear all memories for a specific thread."""
        try:
            query = select(ConversationMemory).where(
                ConversationMemory.thread_id == thread_id
            )
            result = await self.db.execute(query)
            memories = result.scalars().all()
            
            count = len(memories)
            for memory in memories:
                await self.db.delete(memory)
            
            await self.db.commit()
            logger.info(f"Cleared {count} memories for thread {thread_id}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            await self.db.rollback()
            raise
    
    def create_database_provider(
        self,
        thread_id: Optional[str] = None,
        agent_id: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> DatabaseContextProvider:
        """Create a database-backed context provider."""
        return DatabaseContextProvider(
            db=self.db,
            thread_id=thread_id,
            agent_id=agent_id,
            user_id=user_id
        )
