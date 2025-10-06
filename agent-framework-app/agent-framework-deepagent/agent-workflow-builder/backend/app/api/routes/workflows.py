"""
Workflow management API routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.core.database import get_db
from app.models import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowNode,
    WorkflowNodeCreate,
    WorkflowNodeUpdate,
    WorkflowNodeResponse,
    WorkflowEdge,
    WorkflowEdgeCreate,
    WorkflowEdgeUpdate,
    WorkflowEdgeResponse,
)
from app.services.workflow_service import WorkflowService

router = APIRouter()


# Workflow CRUD operations
@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    is_template: Optional[bool] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
) -> List[WorkflowResponse]:
    """List workflows with optional filtering."""
    service = WorkflowService(db)
    return await service.list_workflows(
        skip=skip, 
        limit=limit, 
        is_template=is_template,
        is_public=is_public
    )


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
) -> WorkflowResponse:
    """Create a new workflow."""
    service = WorkflowService(db)
    return await service.create_workflow(workflow_data)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
) -> WorkflowResponse:
    """Get a workflow by ID."""
    service = WorkflowService(db)
    workflow = await service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db)
) -> WorkflowResponse:
    """Update a workflow."""
    service = WorkflowService(db)
    workflow = await service.update_workflow(workflow_id, workflow_data)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a workflow."""
    service = WorkflowService(db)
    success = await service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    workflow_id: int,
    new_name: Optional[str] = None,
    db: Session = Depends(get_db)
) -> WorkflowResponse:
    """Duplicate a workflow."""
    service = WorkflowService(db)
    workflow = await service.duplicate_workflow(workflow_id, new_name)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


# Workflow node operations
@router.get("/{workflow_id}/nodes", response_model=List[WorkflowNodeResponse])
async def list_workflow_nodes(
    workflow_id: int,
    db: Session = Depends(get_db)
) -> List[WorkflowNodeResponse]:
    """List nodes in a workflow."""
    service = WorkflowService(db)
    return await service.list_workflow_nodes(workflow_id)


@router.post("/{workflow_id}/nodes", response_model=WorkflowNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_node(
    workflow_id: int,
    node_data: WorkflowNodeCreate,
    db: Session = Depends(get_db)
) -> WorkflowNodeResponse:
    """Create a new node in a workflow."""
    # Ensure the workflow_id matches
    node_data.workflow_id = workflow_id
    service = WorkflowService(db)
    return await service.create_workflow_node(node_data)


@router.put("/{workflow_id}/nodes/{node_id}", response_model=WorkflowNodeResponse)
async def update_workflow_node(
    workflow_id: int,
    node_id: int,
    node_data: WorkflowNodeUpdate,
    db: Session = Depends(get_db)
) -> WorkflowNodeResponse:
    """Update a workflow node."""
    service = WorkflowService(db)
    node = await service.update_workflow_node(node_id, node_data)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    return node


@router.delete("/{workflow_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_node(
    workflow_id: int,
    node_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a workflow node."""
    service = WorkflowService(db)
    success = await service.delete_workflow_node(node_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )


# Workflow edge operations
@router.get("/{workflow_id}/edges", response_model=List[WorkflowEdgeResponse])
async def list_workflow_edges(
    workflow_id: int,
    db: Session = Depends(get_db)
) -> List[WorkflowEdgeResponse]:
    """List edges in a workflow."""
    service = WorkflowService(db)
    return await service.list_workflow_edges(workflow_id)


@router.post("/{workflow_id}/edges", response_model=WorkflowEdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_edge(
    workflow_id: int,
    edge_data: WorkflowEdgeCreate,
    db: Session = Depends(get_db)
) -> WorkflowEdgeResponse:
    """Create a new edge in a workflow."""
    # Ensure the workflow_id matches
    edge_data.workflow_id = workflow_id
    service = WorkflowService(db)
    return await service.create_workflow_edge(edge_data)


@router.put("/{workflow_id}/edges/{edge_id}", response_model=WorkflowEdgeResponse)
async def update_workflow_edge(
    workflow_id: int,
    edge_id: int,
    edge_data: WorkflowEdgeUpdate,
    db: Session = Depends(get_db)
) -> WorkflowEdgeResponse:
    """Update a workflow edge."""
    service = WorkflowService(db)
    edge = await service.update_workflow_edge(edge_id, edge_data)
    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found"
        )
    return edge


@router.delete("/{workflow_id}/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_edge(
    workflow_id: int,
    edge_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a workflow edge."""
    service = WorkflowService(db)
    success = await service.delete_workflow_edge(edge_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found"
        )


# Workflow validation and visualization
@router.post("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Validate a workflow structure."""
    service = WorkflowService(db)
    result = await service.validate_workflow(workflow_id)
    return result


@router.get("/{workflow_id}/visualization")
async def get_workflow_visualization(
    workflow_id: int,
    format: str = Query("mermaid", regex="^(mermaid|dot|svg|png)$"),
    db: Session = Depends(get_db)
) -> dict:
    """Get workflow visualization in various formats."""
    service = WorkflowService(db)
    result = await service.get_workflow_visualization(workflow_id, format)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return result