"""
Workflow execution API routes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session

from app.core.database import get_db
from app.models import (
    WorkflowExecution,
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
    WorkflowExecutionResponse,
    WorkflowStatus,
)
from app.services.execution_service import ExecutionService

router = APIRouter()


@router.get("/", response_model=List[WorkflowExecutionResponse])
async def list_executions(
    skip: int = 0,
    limit: int = 100,
    workflow_id: int = None,
    status: WorkflowStatus = None,
    db: Session = Depends(get_db)
) -> List[WorkflowExecutionResponse]:
    """List workflow executions with optional filtering."""
    service = ExecutionService(db)
    return await service.list_executions(
        skip=skip,
        limit=limit,
        workflow_id=workflow_id,
        status=status
    )


@router.post("/", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_data: WorkflowExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> WorkflowExecutionResponse:
    """Create and start a new workflow execution."""
    service = ExecutionService(db)
    execution = await service.create_execution(execution_data)
    
    # Start execution in background
    background_tasks.add_task(service.start_execution, execution.id)
    
    return execution


@router.get("/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(
    execution_id: int,
    db: Session = Depends(get_db)
) -> WorkflowExecutionResponse:
    """Get an execution by ID."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    return execution


@router.put("/{execution_id}", response_model=WorkflowExecutionResponse)
async def update_execution(
    execution_id: int,
    execution_data: WorkflowExecutionUpdate,
    db: Session = Depends(get_db)
) -> WorkflowExecutionResponse:
    """Update an execution."""
    service = ExecutionService(db)
    execution = await service.update_execution(execution_id, execution_data)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    return execution


@router.post("/{execution_id}/start")
async def start_execution(
    execution_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """Start a workflow execution."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    if execution.status != WorkflowStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execution can only be started from draft status"
        )
    
    # Start execution in background
    background_tasks.add_task(service.start_execution, execution_id)
    
    return {"message": "Execution started", "execution_id": execution_id}


@router.post("/{execution_id}/pause")
async def pause_execution(
    execution_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Pause a running workflow execution."""
    service = ExecutionService(db)
    success = await service.pause_execution(execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found or cannot be paused"
        )
    
    return {"message": "Execution paused", "execution_id": execution_id}


@router.post("/{execution_id}/resume")
async def resume_execution(
    execution_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """Resume a paused workflow execution."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    if execution.status != WorkflowStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Execution can only be resumed from paused status"
        )
    
    # Resume execution in background
    background_tasks.add_task(service.resume_execution, execution_id)
    
    return {"message": "Execution resumed", "execution_id": execution_id}


@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Cancel a workflow execution."""
    service = ExecutionService(db)
    success = await service.cancel_execution(execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found or cannot be cancelled"
        )
    
    return {"message": "Execution cancelled", "execution_id": execution_id}


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get execution logs."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return execution.execution_log


@router.get("/{execution_id}/status")
async def get_execution_status(
    execution_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Get execution status and progress."""
    service = ExecutionService(db)
    status_info = await service.get_execution_status(execution_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return status_info


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    execution_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete an execution."""
    service = ExecutionService(db)
    success = await service.delete_execution(execution_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )