"""
API routes for workflow checkpoint management.

Provides endpoints for saving, loading, listing, and deleting workflow checkpoints.
Supports Microsoft Agent Framework checkpoint patterns for workflow persistence.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.workflows.checkpoint_storage import DatabaseCheckpointStorage
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class CheckpointResponse(BaseModel):
    """Response model for checkpoint metadata."""
    checkpoint_id: str
    created_at: str
    metadata: Dict[str, Any]


class RestoreRequest(BaseModel):
    """Request model for checkpoint restoration."""
    checkpoint_id: Optional[str] = None


class CheckpointStatusResponse(BaseModel):
    """Response model for checkpoint operations."""
    status: str
    message: Optional[str] = None
    workflow_id: Optional[str] = None
    checkpoint_id: Optional[str] = None


@router.get("/{workflow_id}", response_model=List[CheckpointResponse])
async def list_checkpoints(
    workflow_id: str,
    db: Session = Depends(get_db)
) -> List[CheckpointResponse]:
    """List all checkpoints for a workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        List of checkpoint metadata
        
    Example:
        GET /api/checkpoints/workflow-123
    """
    try:
        storage = DatabaseCheckpointStorage(db)
        checkpoints = await storage.list_checkpoints(workflow_id)
        return [CheckpointResponse(**cp) for cp in checkpoints]
    except Exception as e:
        logger.error(f"Failed to list checkpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/restore", response_model=CheckpointStatusResponse)
async def restore_checkpoint(
    workflow_id: str,
    request: RestoreRequest,
    db: Session = Depends(get_db)
) -> CheckpointStatusResponse:
    """Restore workflow from checkpoint.
    
    Loads the specified checkpoint (or latest if not specified) and returns
    the checkpoint ID that was restored. The caller can use this state to
    resume workflow execution.
    
    Args:
        workflow_id: Workflow to restore
        request: Restoration request with optional checkpoint_id
        db: Database session
        
    Returns:
        Status of restoration operation
        
    Raises:
        HTTPException: If checkpoint not found or restoration fails
        
    Example:
        POST /api/checkpoints/workflow-123/restore
        Body: {"checkpoint_id": "step-5"}  // or omit for latest
    """
    try:
        storage = DatabaseCheckpointStorage(db)
        
        # Load the checkpoint
        state = await storage.load_checkpoint(workflow_id, request.checkpoint_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"No checkpoint found for workflow {workflow_id}"
            )
        
        # In a full implementation, this would rebuild the workflow from state
        # For now, we return success indicating the checkpoint was loaded
        checkpoint_id = request.checkpoint_id or "latest"
        
        logger.info(f"Restored workflow {workflow_id} from checkpoint {checkpoint_id}")
        
        return CheckpointStatusResponse(
            status="restored",
            message=f"Workflow restored from checkpoint {checkpoint_id}",
            workflow_id=workflow_id,
            checkpoint_id=checkpoint_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}/{checkpoint_id}", response_model=CheckpointStatusResponse)
async def delete_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    db: Session = Depends(get_db)
) -> CheckpointStatusResponse:
    """Delete a specific checkpoint.
    
    Args:
        workflow_id: Workflow identifier
        checkpoint_id: Checkpoint to delete
        db: Database session
        
    Returns:
        Status of deletion operation
        
    Raises:
        HTTPException: If checkpoint not found or deletion fails
        
    Example:
        DELETE /api/checkpoints/workflow-123/step-5
    """
    try:
        storage = DatabaseCheckpointStorage(db)
        deleted = await storage.delete_checkpoint(workflow_id, checkpoint_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Checkpoint {checkpoint_id} not found for workflow {workflow_id}"
            )
        
        return CheckpointStatusResponse(
            status="deleted",
            message=f"Checkpoint {checkpoint_id} deleted successfully",
            workflow_id=workflow_id,
            checkpoint_id=checkpoint_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
