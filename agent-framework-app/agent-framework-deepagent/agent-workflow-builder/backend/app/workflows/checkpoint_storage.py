"""
Checkpoint storage for workflow state persistence.

This module provides database-backed checkpoint storage compatible with
Microsoft Agent Framework patterns. It enables save/resume of long-running
workflows by persisting agent threads, executor states, and workflow context.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select
from app.models import WorkflowCheckpoint
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseCheckpointStorage:
    """PostgreSQL/SQLite-backed checkpoint storage compatible with Agent Framework.
    
    This storage implementation follows Microsoft Agent Framework's checkpoint patterns:
    - Saves complete workflow state at superstep boundaries
    - Serializes agent threads for persistence
    - Captures executor states and context
    - Enables workflow resume from any checkpoint
    
    Usage:
        storage = DatabaseCheckpointStorage(db_session)
        await storage.save_checkpoint(
            workflow_id="workflow-123",
            checkpoint_id="step-5",
            state_data={"agents": {...}, "context": {...}}
        )
        
        # Later, restore from checkpoint
        state = await storage.load_checkpoint("workflow-123", "step-5")
    """
    
    def __init__(self, db: Session):
        """Initialize checkpoint storage with database session.
        
        Args:
            db: SQLModel database session
        """
        self.db = db
    
    async def save_checkpoint(
        self, 
        workflow_id: str, 
        checkpoint_id: str, 
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save workflow checkpoint to database.
        
        Args:
            workflow_id: Unique workflow identifier
            checkpoint_id: Checkpoint identifier (e.g., "step_3", "agent_1_complete")
            state_data: Complete workflow state including:
                - Agent threads and their message histories
                - Executor states and configurations
                - Workflow context and variables
                - Current execution position
            metadata: Optional metadata (timestamp, user_id, tags, etc.)
            
        Raises:
            Exception: If checkpoint save fails
        """
        try:
            checkpoint = WorkflowCheckpoint(
                workflow_id=workflow_id,
                checkpoint_id=checkpoint_id,
                state_data=state_data,
                checkpoint_metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            self.db.add(checkpoint)
            self.db.commit()
            self.db.refresh(checkpoint)
            logger.info(f"Saved checkpoint {checkpoint_id} for workflow {workflow_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            self.db.rollback()
            raise
    
    async def load_checkpoint(
        self, 
        workflow_id: str, 
        checkpoint_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Load checkpoint from database.
        
        Args:
            workflow_id: Workflow identifier
            checkpoint_id: Specific checkpoint or None for latest
            
        Returns:
            Checkpoint state data containing:
                - Agent threads with message histories
                - Executor states
                - Workflow context
            Returns None if no checkpoint found
            
        Raises:
            Exception: If checkpoint load fails
        """
        try:
            query = select(WorkflowCheckpoint).where(
                WorkflowCheckpoint.workflow_id == workflow_id
            )
            
            if checkpoint_id:
                query = query.where(WorkflowCheckpoint.checkpoint_id == checkpoint_id)
            else:
                # Load latest checkpoint if no specific ID provided
                query = query.order_by(WorkflowCheckpoint.created_at.desc())
            
            result = self.db.exec(query)
            checkpoint = result.first()
            
            if checkpoint:
                logger.info(f"Loaded checkpoint {checkpoint.checkpoint_id} for workflow {workflow_id}")
                return checkpoint.state_data
            
            logger.warning(f"No checkpoint found for workflow {workflow_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            raise
    
    async def list_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """List all checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoint metadata dictionaries with:
                - checkpoint_id: Checkpoint identifier
                - created_at: Creation timestamp
                - metadata: Associated metadata
        """
        try:
            query = select(WorkflowCheckpoint).where(
                WorkflowCheckpoint.workflow_id == workflow_id
            ).order_by(WorkflowCheckpoint.created_at.desc())
            
            result = self.db.exec(query)
            checkpoints = result.all()
            
            return [
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "created_at": cp.created_at.isoformat(),
                    "metadata": cp.checkpoint_metadata
                }
                for cp in checkpoints
            ]
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            raise
    
    async def delete_checkpoint(self, workflow_id: str, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint.
        
        Args:
            workflow_id: Workflow identifier
            checkpoint_id: Checkpoint to delete
            
        Returns:
            True if checkpoint was deleted, False if not found
            
        Raises:
            Exception: If deletion fails
        """
        try:
            query = select(WorkflowCheckpoint).where(
                WorkflowCheckpoint.workflow_id == workflow_id,
                WorkflowCheckpoint.checkpoint_id == checkpoint_id
            )
            result = self.db.exec(query)
            checkpoint = result.first()
            
            if checkpoint:
                self.db.delete(checkpoint)
                self.db.commit()
                logger.info(f"Deleted checkpoint {checkpoint_id} for workflow {workflow_id}")
                return True
            
            logger.warning(f"Checkpoint {checkpoint_id} not found for workflow {workflow_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")
            self.db.rollback()
            raise
