"""
Execution service for managing workflow executions.
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    WorkflowExecution, WorkflowExecutionCreate, WorkflowExecutionUpdate, WorkflowExecutionResponse,
    WorkflowStatus, Workflow
)
from app.workflows.workflow_executor import WorkflowExecutor
from app.services.workflow_service import WorkflowService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionService:
    """Service for managing workflow executions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
        self.workflow_executor = WorkflowExecutor()
        self.running_executions: Dict[int, asyncio.Task] = {}
    
    async def list_executions(
        self,
        skip: int = 0,
        limit: int = 100,
        workflow_id: Optional[int] = None,
        status: Optional[WorkflowStatus] = None
    ) -> List[WorkflowExecutionResponse]:
        """List workflow executions with optional filtering."""
        statement = select(WorkflowExecution).offset(skip).limit(limit)
        
        if workflow_id is not None:
            statement = statement.where(WorkflowExecution.workflow_id == workflow_id)
        if status is not None:
            statement = statement.where(WorkflowExecution.status == status)
        
        result = self.db.exec(statement)
        executions = result.all()
        
        return [WorkflowExecutionResponse.from_orm(execution) for execution in executions]
    
    async def create_execution(self, execution_data: WorkflowExecutionCreate) -> WorkflowExecutionResponse:
        """Create a new workflow execution."""
        execution = WorkflowExecution(**execution_data.dict())
        execution.created_at = datetime.utcnow()
        execution.status = WorkflowStatus.DRAFT
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        logger.info(f"Created workflow execution: {execution.id}")
        
        return WorkflowExecutionResponse.from_orm(execution)
    
    async def get_execution(self, execution_id: int) -> Optional[WorkflowExecutionResponse]:
        """Get an execution by ID."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return None
        
        return WorkflowExecutionResponse.from_orm(execution)
    
    async def update_execution(self, execution_id: int, execution_data: WorkflowExecutionUpdate) -> Optional[WorkflowExecutionResponse]:
        """Update an execution."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return None
        
        # Update fields
        update_data = execution_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(execution, field, value)
        
        execution.updated_at = datetime.utcnow()
        
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        logger.info(f"Updated workflow execution: {execution.id}")
        
        return WorkflowExecutionResponse.from_orm(execution)
    
    async def delete_execution(self, execution_id: int) -> bool:
        """Delete an execution."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return False
        
        # Cancel if running
        if execution_id in self.running_executions:
            self.running_executions[execution_id].cancel()
            del self.running_executions[execution_id]
        
        self.db.delete(execution)
        self.db.commit()
        
        logger.info(f"Deleted workflow execution: {execution_id}")
        
        return True
    
    async def start_execution(self, execution_id: int) -> bool:
        """Start a workflow execution."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return False
        
        if execution.status not in [WorkflowStatus.DRAFT, WorkflowStatus.PAUSED]:
            return False
        
        # Get workflow
        workflow = await self.workflow_service.get_workflow(execution.workflow_id)
        if not workflow:
            return False
        
        # Update status
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.utcnow()
        execution.execution_log = execution.execution_log or []
        execution.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_started",
            "message": "Workflow execution started"
        })
        
        self.db.add(execution)
        self.db.commit()
        
        # Start execution task
        task = asyncio.create_task(self._execute_workflow(execution_id, workflow))
        self.running_executions[execution_id] = task
        
        logger.info(f"Started workflow execution: {execution_id}")
        
        return True
    
    async def pause_execution(self, execution_id: int) -> bool:
        """Pause a running workflow execution."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution or execution.status != WorkflowStatus.RUNNING:
            return False
        
        # Cancel the running task
        if execution_id in self.running_executions:
            self.running_executions[execution_id].cancel()
            del self.running_executions[execution_id]
        
        # Update status
        execution.status = WorkflowStatus.PAUSED
        execution.execution_log = execution.execution_log or []
        execution.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_paused",
            "message": "Workflow execution paused"
        })
        
        self.db.add(execution)
        self.db.commit()
        
        logger.info(f"Paused workflow execution: {execution_id}")
        
        return True
    
    async def resume_execution(self, execution_id: int) -> bool:
        """Resume a paused workflow execution."""
        return await self.start_execution(execution_id)
    
    async def cancel_execution(self, execution_id: int) -> bool:
        """Cancel a workflow execution."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return False
        
        # Cancel the running task
        if execution_id in self.running_executions:
            self.running_executions[execution_id].cancel()
            del self.running_executions[execution_id]
        
        # Update status
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        execution.execution_log = execution.execution_log or []
        execution.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "execution_cancelled",
            "message": "Workflow execution cancelled"
        })
        
        self.db.add(execution)
        self.db.commit()
        
        logger.info(f"Cancelled workflow execution: {execution_id}")
        
        return True
    
    async def get_execution_status(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution status and progress."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return None
        
        is_running = execution_id in self.running_executions
        
        return {
            "execution_id": execution_id,
            "status": execution.status,
            "is_running": is_running,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "progress": self._calculate_progress(execution),
            "current_node": self._get_current_node(execution),
            "error_message": execution.error_message,
        }
    
    async def _execute_workflow(self, execution_id: int, workflow) -> None:
        """Execute a workflow (internal method)."""
        execution = self.db.get(WorkflowExecution, execution_id)
        if not execution:
            return
        
        try:
            # Execute the workflow
            result = await self.workflow_executor.execute(
                workflow, 
                execution.input_data,
                execution_id=execution_id
            )
            
            # Update execution with results
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.output_data = result
            execution.execution_log = execution.execution_log or []
            execution.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "execution_completed",
                "message": "Workflow execution completed successfully"
            })
            
            logger.info(f"Completed workflow execution: {execution_id}")
            
        except asyncio.CancelledError:
            # Execution was cancelled
            logger.info(f"Workflow execution cancelled: {execution_id}")
            return
            
        except Exception as e:
            # Execution failed
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.execution_log = execution.execution_log or []
            execution.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "execution_failed",
                "message": f"Workflow execution failed: {str(e)}"
            })
            
            logger.error(f"Failed workflow execution: {execution_id} - {str(e)}")
        
        finally:
            # Clean up
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
            
            self.db.add(execution)
            self.db.commit()
    
    def _calculate_progress(self, execution: WorkflowExecution) -> float:
        """Calculate execution progress (0.0 to 1.0)."""
        if execution.status == WorkflowStatus.DRAFT:
            return 0.0
        elif execution.status == WorkflowStatus.RUNNING:
            # TODO: Implement actual progress calculation based on completed nodes
            return 0.5
        elif execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED]:
            return 1.0
        else:
            return 0.0
    
    def _get_current_node(self, execution: WorkflowExecution) -> Optional[str]:
        """Get the currently executing node."""
        # TODO: Implement actual current node tracking
        if execution.status == WorkflowStatus.RUNNING:
            return "processing"
        return None