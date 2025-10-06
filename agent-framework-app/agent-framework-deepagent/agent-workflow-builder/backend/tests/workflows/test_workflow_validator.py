"""Tests for WorkflowValidator."""
import pytest
from typing import List
from app.workflows.workflow_validator import WorkflowValidator
from app.models import WorkflowResponse, WorkflowNodeResponse, WorkflowEdgeResponse, ExecutorType


@pytest.fixture
def validator():
    """Create a WorkflowValidator instance."""
    return WorkflowValidator()


@pytest.fixture
def valid_simple_workflow():
    """Create a valid simple workflow."""
    nodes = [
        WorkflowNodeResponse(
            id=1,
            workflow_id=1,
            name="Start",
            node_type="start",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"is_start": True},
            position_x=0,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=2,
            workflow_id=1,
            name="Process",
            node_type="agent",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"agent_id": 1},
            position_x=100,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=3,
            workflow_id=1,
            name="End",
            node_type="end",
            executor_type=ExecutorType.SEQUENTIAL,
            config={},
            position_x=200,
            position_y=0,
            is_output_node=True
        ),
    ]
    
    edges = [
        WorkflowEdgeResponse(
            id=1,
            workflow_id=1,
            source_node_id=1,
            target_node_id=2,
            condition=None
        ),
        WorkflowEdgeResponse(
            id=2,
            workflow_id=1,
            source_node_id=2,
            target_node_id=3,
            condition=None
        ),
    ]
    
    return WorkflowResponse(
        id=1,
        name="Simple Workflow",
        description="A simple test workflow",
        status="draft",
        nodes=nodes,
        edges=edges
    )


@pytest.fixture
def workflow_with_cycle():
    """Create a workflow with a cycle."""
    nodes = [
        WorkflowNodeResponse(
            id=1,
            workflow_id=1,
            name="Start",
            node_type="start",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"is_start": True},
            position_x=0,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=2,
            workflow_id=1,
            name="Node A",
            node_type="agent",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"agent_id": 1},
            position_x=100,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=3,
            workflow_id=1,
            name="Node B",
            node_type="agent",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"agent_id": 2},
            position_x=200,
            position_y=0,
            is_output_node=False
        ),
    ]
    
    # Create a cycle: Start -> A -> B -> A
    edges = [
        WorkflowEdgeResponse(
            id=1,
            workflow_id=1,
            source_node_id=1,
            target_node_id=2,
            condition=None
        ),
        WorkflowEdgeResponse(
            id=2,
            workflow_id=1,
            source_node_id=2,
            target_node_id=3,
            condition=None
        ),
        WorkflowEdgeResponse(
            id=3,
            workflow_id=1,
            source_node_id=3,
            target_node_id=2,  # Back to node A - creates cycle
            condition=None
        ),
    ]
    
    return WorkflowResponse(
        id=1,
        name="Workflow with Cycle",
        description="A workflow with a cycle",
        status="draft",
        nodes=nodes,
        edges=edges
    )


@pytest.fixture
def workflow_with_orphaned_node():
    """Create a workflow with an orphaned node."""
    nodes = [
        WorkflowNodeResponse(
            id=1,
            workflow_id=1,
            name="Start",
            node_type="start",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"is_start": True},
            position_x=0,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=2,
            workflow_id=1,
            name="Connected Node",
            node_type="agent",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"agent_id": 1},
            position_x=100,
            position_y=0,
            is_output_node=False
        ),
        WorkflowNodeResponse(
            id=3,
            workflow_id=1,
            name="Orphaned Node",
            node_type="agent",
            executor_type=ExecutorType.SEQUENTIAL,
            config={"agent_id": 2},
            position_x=100,
            position_y=100,
            is_output_node=False
        ),
    ]
    
    # Only connect start to node 2, leave node 3 orphaned
    edges = [
        WorkflowEdgeResponse(
            id=1,
            workflow_id=1,
            source_node_id=1,
            target_node_id=2,
            condition=None
        ),
    ]
    
    return WorkflowResponse(
        id=1,
        name="Workflow with Orphan",
        description="A workflow with an orphaned node",
        status="draft",
        nodes=nodes,
        edges=edges
    )


class TestWorkflowValidator:
    """Test suite for WorkflowValidator."""
    
    @pytest.mark.asyncio
    async def test_valid_simple_workflow(self, validator, valid_simple_workflow):
        """Test validation of a valid simple workflow."""
        result = await validator.validate(valid_simple_workflow)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_workflow_without_nodes(self, validator):
        """Test validation of a workflow without nodes."""
        workflow = WorkflowResponse(
            id=1,
            name="Empty Workflow",
            description="A workflow with no nodes",
            status="draft",
            nodes=[],
            edges=[]
        )
        
        result = await validator.validate(workflow)
        
        assert result["valid"] is False
        assert any("at least one node" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_workflow_without_start_node(self, validator):
        """Test validation of a workflow without a start node."""
        nodes = [
            WorkflowNodeResponse(
                id=1,
                workflow_id=1,
                name="Process",
                node_type="agent",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"agent_id": 1},
                position_x=0,
                position_y=0,
                is_output_node=False
            ),
        ]
        
        workflow = WorkflowResponse(
            id=1,
            name="No Start Workflow",
            description="A workflow without start node",
            status="draft",
            nodes=nodes,
            edges=[]
        )
        
        result = await validator.validate(workflow)
        
        assert result["valid"] is False
        assert any("start node" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_workflow_with_cycle(self, validator, workflow_with_cycle):
        """Test validation of a workflow with a cycle."""
        result = await validator.validate(workflow_with_cycle)
        
        assert result["valid"] is False
        assert any("cycle" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_workflow_with_orphaned_node(self, validator, workflow_with_orphaned_node):
        """Test validation of a workflow with an orphaned node."""
        result = await validator.validate(workflow_with_orphaned_node)
        
        # Orphaned nodes generate warnings, not errors
        assert any("orphaned" in warning.lower() for warning in result.get("warnings", []))
    
    @pytest.mark.asyncio
    async def test_workflow_without_output_node(self, validator):
        """Test validation of a workflow without output nodes."""
        nodes = [
            WorkflowNodeResponse(
                id=1,
                workflow_id=1,
                name="Start",
                node_type="start",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"is_start": True},
                position_x=0,
                position_y=0,
                is_output_node=False
            ),
            WorkflowNodeResponse(
                id=2,
                workflow_id=1,
                name="Process",
                node_type="agent",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"agent_id": 1},
                position_x=100,
                position_y=0,
                is_output_node=False  # Not marked as output
            ),
        ]
        
        edges = [
            WorkflowEdgeResponse(
                id=1,
                workflow_id=1,
                source_node_id=1,
                target_node_id=2,
                condition=None
            ),
        ]
        
        workflow = WorkflowResponse(
            id=1,
            name="No Output Workflow",
            description="A workflow without output nodes",
            status="draft",
            nodes=nodes,
            edges=edges
        )
        
        result = await validator.validate(workflow)
        
        # No output nodes should generate a warning
        assert any("output" in warning.lower() for warning in result.get("warnings", []))
    
    @pytest.mark.asyncio
    async def test_node_config_validation(self, validator):
        """Test validation of node configurations."""
        nodes = [
            WorkflowNodeResponse(
                id=1,
                workflow_id=1,
                name="Start",
                node_type="start",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"is_start": True},
                position_x=0,
                position_y=0,
                is_output_node=False
            ),
            WorkflowNodeResponse(
                id=2,
                workflow_id=1,
                name="Agent Node",
                node_type="agent",
                executor_type=ExecutorType.SEQUENTIAL,
                config={},  # Missing required agent_id
                position_x=100,
                position_y=0,
                is_output_node=False
            ),
        ]
        
        edges = [
            WorkflowEdgeResponse(
                id=1,
                workflow_id=1,
                source_node_id=1,
                target_node_id=2,
                condition=None
            ),
        ]
        
        workflow = WorkflowResponse(
            id=1,
            name="Invalid Config Workflow",
            description="A workflow with invalid node config",
            status="draft",
            nodes=nodes,
            edges=edges
        )
        
        result = await validator.validate(workflow)
        
        # Should have configuration errors
        assert result["valid"] is False
        assert any("agent_id" in error.lower() for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_multiple_start_nodes(self, validator):
        """Test validation of a workflow with multiple start nodes."""
        nodes = [
            WorkflowNodeResponse(
                id=1,
                workflow_id=1,
                name="Start 1",
                node_type="start",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"is_start": True},
                position_x=0,
                position_y=0,
                is_output_node=False
            ),
            WorkflowNodeResponse(
                id=2,
                workflow_id=1,
                name="Start 2",
                node_type="start",
                executor_type=ExecutorType.SEQUENTIAL,
                config={"is_start": True},
                position_x=0,
                position_y=100,
                is_output_node=False
            ),
        ]
        
        workflow = WorkflowResponse(
            id=1,
            name="Multiple Starts Workflow",
            description="A workflow with multiple start nodes",
            status="draft",
            nodes=nodes,
            edges=[]
        )
        
        result = await validator.validate(workflow)
        
        assert result["valid"] is False
        assert any("multiple start" in error.lower() for error in result["errors"])
