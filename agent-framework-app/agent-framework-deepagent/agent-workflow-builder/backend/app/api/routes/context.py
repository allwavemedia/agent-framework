"""
API routes for context providers and conversation memory management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.services.context_service import ContextService
from app.models import (
    ContextProviderConfigCreate,
    ContextProviderConfigResponse,
    ConversationMemory
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/context", tags=["context"])


@router.post("/providers", response_model=ContextProviderConfigResponse)
async def create_provider_config(
    config: ContextProviderConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new context provider configuration.
    
    Args:
        config: Context provider configuration
        db: Database session
    
    Returns:
        Created context provider configuration
    """
    try:
        service = ContextService(db)
        provider_config = await service.create_provider_config(
            name=config.name,
            provider_type=config.provider_type,
            config=config.config
        )
        
        return ContextProviderConfigResponse(
            id=provider_config.id,
            name=provider_config.name,
            provider_type=provider_config.provider_type,
            config=provider_config.config,
            is_active=provider_config.is_active,
            created_at=provider_config.created_at,
            updated_at=provider_config.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error creating provider config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[ContextProviderConfigResponse])
async def list_provider_configs(
    db: Session = Depends(get_db)
):
    """
    List all context provider configurations.
    
    Args:
        db: Database session
    
    Returns:
        List of context provider configurations
    """
    try:
        service = ContextService(db)
        configs = await service.list_provider_configs()
        
        return [
            ContextProviderConfigResponse(
                id=config.id,
                name=config.name,
                provider_type=config.provider_type,
                config=config.config,
                is_active=config.is_active,
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            for config in configs
        ]
        
    except Exception as e:
        logger.error(f"Error listing provider configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{config_id}", response_model=ContextProviderConfigResponse)
async def get_provider_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific context provider configuration.
    
    Args:
        config_id: Context provider configuration ID
        db: Database session
    
    Returns:
        Context provider configuration
    """
    try:
        service = ContextService(db)
        config = await service.get_provider_config(config_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Provider config not found")
        
        return ContextProviderConfigResponse(
            id=config.id,
            name=config.name,
            provider_type=config.provider_type,
            config=config.config,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/thread/{thread_id}")
async def get_thread_memories(
    thread_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get conversation memories for a specific thread.
    
    Args:
        thread_id: Thread identifier
        limit: Maximum number of memories to return
        db: Database session
    
    Returns:
        List of conversation memories
    """
    try:
        service = ContextService(db)
        memories = await service.get_thread_memories(thread_id, limit)
        
        return {
            "thread_id": thread_id,
            "count": len(memories),
            "memories": [
                {
                    "id": mem.id,
                    "memory_key": mem.memory_key,
                    "memory_value": mem.memory_value,
                    "created_at": mem.created_at,
                    "user_id": mem.user_id,
                    "agent_id": mem.agent_id
                }
                for mem in memories
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting thread memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/user/{user_id}")
async def get_user_memories(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get conversation memories for a specific user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of memories to return
        db: Database session
    
    Returns:
        List of conversation memories
    """
    try:
        service = ContextService(db)
        memories = await service.get_user_memories(user_id, limit)
        
        return {
            "user_id": user_id,
            "count": len(memories),
            "memories": [
                {
                    "id": mem.id,
                    "thread_id": mem.thread_id,
                    "memory_key": mem.memory_key,
                    "memory_value": mem.memory_value,
                    "created_at": mem.created_at,
                    "agent_id": mem.agent_id
                }
                for mem in memories
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/thread/{thread_id}")
async def clear_thread_memories(
    thread_id: str,
    db: Session = Depends(get_db)
):
    """
    Clear all memories for a specific thread.
    
    Args:
        thread_id: Thread identifier
        db: Database session
    
    Returns:
        Number of memories cleared
    """
    try:
        service = ContextService(db)
        count = await service.clear_thread_memories(thread_id)
        
        return {
            "thread_id": thread_id,
            "cleared_count": count,
            "message": f"Cleared {count} memories for thread {thread_id}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing thread memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for context service."""
    return {
        "status": "healthy",
        "service": "context-provider",
        "features": [
            "database_context_provider",
            "conversation_memory",
            "provider_configuration"
        ]
    }
