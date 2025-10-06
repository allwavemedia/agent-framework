"""
Workflow service for managing workflows, nodes, and edges.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from app.models import (
    Workflow, WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowNode, WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeResponse,
    WorkflowEdge, WorkflowEdgeCreate, WorkflowEdgeUpdate, WorkflowEdgeResponse,
)
from app.workflows.workflow_builder import WorkflowBuilder
from app.workflows.workflow_validator import WorkflowValidator
from app.workflows.workflow_visualizer import WorkflowVisualizer
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowService:
    """Service for managing workflows."""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_builder = WorkflowBuilder()
        self.workflow_validator = WorkflowValidator()
        self.workflow_visualizer = WorkflowVisualizer()
    
    # Workflow CRUD operations
    async def list_workflows(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_template: Optional[bool] = None,
        is_public: Optional[bool] = None
    ) -> List[WorkflowResponse]:
        """List workflows with optional filtering."""
        statement = select(Workflow).offset(skip).limit(limit)
        
        if is_template is not None:
            statement = statement.where(Workflow.is_template == is_template)
        if is_public is not None:
            statement = statement.where(Workflow.is_public == is_public)
        
        result = self.db.exec(statement)
        workflows = result.all()
        
        # Load related data
        workflow_responses = []
        for workflow in workflows:
            workflow_response = WorkflowResponse.from_orm(workflow)
            workflow_response.nodes = await self.list_workflow_nodes(workflow.id)
            workflow_response.edges = await self.list_workflow_edges(workflow.id)
            workflow_responses.append(workflow_response)
        
        return workflow_responses
    
    async def create_workflow(self, workflow_data: WorkflowCreate) -> WorkflowResponse:
        """Create a new workflow."""
        workflow = Workflow(**workflow_data.dict())
        workflow.created_at = datetime.utcnow()
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")
        
        workflow_response = WorkflowResponse.from_orm(workflow)
        workflow_response.nodes = []
        workflow_response.edges = []
        
        return workflow_response
    
    async def get_workflow(self, workflow_id: int) -> Optional[WorkflowResponse]:
        """Get a workflow by ID."""
        workflow = self.db.get(Workflow, workflow_id)
        if not workflow:
            return None
        
        workflow_response = WorkflowResponse.from_orm(workflow)
        workflow_response.nodes = await self.list_workflow_nodes(workflow_id)
        workflow_response.edges = await self.list_workflow_edges(workflow_id)
        
        return workflow_response
    
    async def update_workflow(self, workflow_id: int, workflow_data: WorkflowUpdate) -> Optional[WorkflowResponse]:
        """Update a workflow."""
        workflow = self.db.get(Workflow, workflow_id)
        if not workflow:
            return None
        
        # Update fields
        update_data = workflow_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        workflow.updated_at = datetime.utcnow()
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        logger.info(f"Updated workflow: {workflow.name} (ID: {workflow.id})")
        
        workflow_response = WorkflowResponse.from_orm(workflow)
        workflow_response.nodes = await self.list_workflow_nodes(workflow_id)
        workflow_response.edges = await self.list_workflow_edges(workflow_id)
        
        return workflow_response
    
    async def delete_workflow(self, workflow_id: int) -> bool:
        """Delete a workflow."""
        workflow = self.db.get(Workflow, workflow_id)
        if not workflow:
            return False
        
        # Delete related nodes and edges first
        nodes_statement = select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id)
        nodes = self.db.exec(nodes_statement).all()
        for node in nodes:
            self.db.delete(node)
        
        edges_statement = select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id)
        edges = self.db.exec(edges_statement).all()
        for edge in edges:
            self.db.delete(edge)
        
        # Delete workflow
        self.db.delete(workflow)
        self.db.commit()
        
        logger.info(f"Deleted workflow: {workflow.name} (ID: {workflow_id})")
        
        return True
    
    async def duplicate_workflow(self, workflow_id: int, new_name: Optional[str] = None) -> Optional[WorkflowResponse]:
        """Duplicate a workflow."""
        original_workflow = self.db.get(Workflow, workflow_id)
        if not original_workflow:
            return None
        
        # Create new workflow
        new_workflow_data = WorkflowCreate(
            name=new_name or f"{original_workflow.name} (Copy)",
            description=original_workflow.description,
            version="1.0.0",
            tags=original_workflow.tags,
            is_template=False,
            is_public=False,
        )
        
        new_workflow = await self.create_workflow(new_workflow_data)
        
        # Copy nodes
        original_nodes = await self.list_workflow_nodes(workflow_id)
        node_id_mapping = {}
        
        for original_node in original_nodes:
            new_node_data = WorkflowNodeCreate(
                workflow_id=new_workflow.id,
                name=original_node.name,
                executor_type=original_node.executor_type,
                position_x=original_node.position_x,
                position_y=original_node.position_y,
                config=original_node.config,
                is_start_node=original_node.is_start_node,
                agent_id=original_node.agent_id,
            )
            
            new_node = await self.create_workflow_node(new_node_data)
            node_id_mapping[original_node.id] = new_node.id
        
        # Copy edges
        original_edges = await self.list_workflow_edges(workflow_id)
        for original_edge in original_edges:
            new_edge_data = WorkflowEdgeCreate(
                workflow_id=new_workflow.id,
                source_node_id=node_id_mapping[original_edge.source_node_id],
                target_node_id=node_id_mapping[original_edge.target_node_id],
                label=original_edge.label,
                condition=original_edge.condition,
                config=original_edge.config,
            )
            
            await self.create_workflow_edge(new_edge_data)
        
        logger.info(f"Duplicated workflow: {original_workflow.name} -> {new_workflow.name}")
        
        return await self.get_workflow(new_workflow.id)
    
    # Node operations
    async def list_workflow_nodes(self, workflow_id: int) -> List[WorkflowNodeResponse]:
        """List nodes in a workflow."""
        statement = select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id)
        result = self.db.exec(statement)
        nodes = result.all()
        
        return [WorkflowNodeResponse.from_orm(node) for node in nodes]
    
    async def create_workflow_node(self, node_data: WorkflowNodeCreate) -> WorkflowNodeResponse:
        """Create a new workflow node."""
        node = WorkflowNode(**node_data.dict())
        node.created_at = datetime.utcnow()
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        logger.info(f"Created workflow node: {node.name} (ID: {node.id})")
        
        return WorkflowNodeResponse.from_orm(node)
    
    async def update_workflow_node(self, node_id: int, node_data: WorkflowNodeUpdate) -> Optional[WorkflowNodeResponse]:
        """Update a workflow node."""
        node = self.db.get(WorkflowNode, node_id)
        if not node:
            return None
        
        # Update fields
        update_data = node_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)
        
        node.updated_at = datetime.utcnow()
        
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        
        logger.info(f"Updated workflow node: {node.name} (ID: {node.id})")
        
        return WorkflowNodeResponse.from_orm(node)
    
    async def delete_workflow_node(self, node_id: int) -> bool:
        """Delete a workflow node."""
        node = self.db.get(WorkflowNode, node_id)
        if not node:
            return False
        
        # Delete related edges first
        source_edges_statement = select(WorkflowEdge).where(WorkflowEdge.source_node_id == node_id)
        source_edges = self.db.exec(source_edges_statement).all()
        for edge in source_edges:
            self.db.delete(edge)
        
        target_edges_statement = select(WorkflowEdge).where(WorkflowEdge.target_node_id == node_id)
        target_edges = self.db.exec(target_edges_statement).all()
        for edge in target_edges:
            self.db.delete(edge)
        
        # Delete node
        self.db.delete(node)
        self.db.commit()
        
        logger.info(f"Deleted workflow node: {node.name} (ID: {node_id})")
        
        return True
    
    # Edge operations
    async def list_workflow_edges(self, workflow_id: int) -> List[WorkflowEdgeResponse]:
        """List edges in a workflow."""
        statement = select(WorkflowEdge).where(WorkflowEdge.workflow_id == workflow_id)
        result = self.db.exec(statement)
        edges = result.all()
        
        return [WorkflowEdgeResponse.from_orm(edge) for edge in edges]
    
    async def create_workflow_edge(self, edge_data: WorkflowEdgeCreate) -> WorkflowEdgeResponse:
        """Create a new workflow edge."""
        edge = WorkflowEdge(**edge_data.dict())
        edge.created_at = datetime.utcnow()
        
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        
        logger.info(f"Created workflow edge: {edge.id}")
        
        return WorkflowEdgeResponse.from_orm(edge)
    
    async def update_workflow_edge(self, edge_id: int, edge_data: WorkflowEdgeUpdate) -> Optional[WorkflowEdgeResponse]:
        """Update a workflow edge."""
        edge = self.db.get(WorkflowEdge, edge_id)
        if not edge:
            return None
        
        # Update fields
        update_data = edge_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(edge, field, value)
        
        edge.updated_at = datetime.utcnow()
        
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        
        logger.info(f"Updated workflow edge: {edge.id}")
        
        return WorkflowEdgeResponse.from_orm(edge)
    
    async def delete_workflow_edge(self, edge_id: int) -> bool:
        """Delete a workflow edge."""
        edge = self.db.get(WorkflowEdge, edge_id)
        if not edge:
            return False
        
        self.db.delete(edge)
        self.db.commit()
        
        logger.info(f"Deleted workflow edge: {edge_id}")
        
        return True
    
    # Workflow validation and visualization
    async def validate_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """Validate a workflow structure."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return {"valid": False, "errors": ["Workflow not found"]}
        
        return await self.workflow_validator.validate(workflow)
    
    async def get_workflow_visualization(self, workflow_id: int, format: str) -> Optional[Dict[str, Any]]:
        """Get workflow visualization in various formats."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        return await self.workflow_visualizer.generate(workflow, format)