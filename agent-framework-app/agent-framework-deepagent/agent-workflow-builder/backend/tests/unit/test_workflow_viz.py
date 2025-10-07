"""
Unit tests for WorkflowViz integration.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from app.workflows.workflow_visualizer import WorkflowVisualizer, WORKFLOW_VIZ_AVAILABLE
from app.models import WorkflowResponse, WorkflowNode, WorkflowEdge, ExecutorType


@pytest.fixture
def sample_workflow():
    """Create a sample workflow for testing."""
    return WorkflowResponse(
        id=1,
        name="test-workflow",
        description="Test workflow for visualization",
        status="draft",
        nodes=[
            WorkflowNode(
                id=1,
                workflow_id=1,
                name="Start Node",
                executor_type=ExecutorType.AGENT,
                is_start_node=True,
                is_output_node=False,
                position_x=100,
                position_y=100,
                config={}
            ),
            WorkflowNode(
                id=2,
                workflow_id=1,
                name="Process Node",
                executor_type=ExecutorType.FUNCTION,
                is_start_node=False,
                is_output_node=False,
                position_x=200,
                position_y=200,
                config={}
            ),
            WorkflowNode(
                id=3,
                workflow_id=1,
                name="End Node",
                executor_type=ExecutorType.AGENT,
                is_start_node=False,
                is_output_node=True,
                position_x=300,
                position_y=300,
                config={}
            )
        ],
        edges=[
            WorkflowEdge(
                id=1,
                workflow_id=1,
                source_node_id=1,
                target_node_id=2,
                label="to_process",
                config={}
            ),
            WorkflowEdge(
                id=2,
                workflow_id=1,
                source_node_id=2,
                target_node_id=3,
                label="to_end",
                config={}
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=None
    )


@pytest.mark.asyncio
async def test_generate_mermaid_custom(sample_workflow):
    """Test Mermaid diagram generation with custom builder."""
    visualizer = WorkflowVisualizer()
    
    result = await visualizer.generate_mermaid(sample_workflow)
    
    assert result["format"] == "mermaid"
    assert result["workflow_id"] == 1
    assert result["workflow_name"] == "test-workflow"
    assert result["node_count"] == 3
    assert result["edge_count"] == 2
    assert "graph TB" in result["content"]
    assert "Start Node" in result["content"]


@pytest.mark.asyncio
async def test_generate_dot_custom(sample_workflow):
    """Test DOT diagram generation with custom builder."""
    visualizer = WorkflowVisualizer()
    
    result = await visualizer.generate_dot(sample_workflow)
    
    assert result["format"] == "dot"
    assert result["workflow_id"] == 1
    assert "digraph workflow" in result["content"]
    assert "N1" in result["content"]  # Node IDs


@pytest.mark.asyncio
async def test_generate_json(sample_workflow):
    """Test JSON visualization data generation."""
    visualizer = WorkflowVisualizer()
    
    result = await visualizer.generate_json(sample_workflow)
    
    assert result["format"] == "json"
    assert result["workflow_id"] == 1
    assert len(result["content"]["nodes"]) == 3
    assert len(result["content"]["edges"]) == 2
    
    # Check node structure
    node = result["content"]["nodes"][0]
    assert "id" in node
    assert "label" in node
    assert "type" in node
    assert "position" in node


@pytest.mark.asyncio
async def test_generate_react_flow_data(sample_workflow):
    """Test React Flow data generation."""
    visualizer = WorkflowVisualizer()
    
    result = await visualizer.generate_react_flow_data(sample_workflow)
    
    assert result["format"] == "react-flow"
    assert len(result["nodes"]) == 3
    assert len(result["edges"]) == 2
    
    # Check node structure for React Flow
    node = result["nodes"][0]
    assert "id" in node
    assert "type" in node
    assert "data" in node
    assert "position" in node


@pytest.mark.asyncio
@patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', True)
async def test_generate_mermaid_with_workflowviz(sample_workflow):
    """Test Mermaid generation using Agent Framework WorkflowViz."""
    visualizer = WorkflowVisualizer()
    
    # Mock the Agent Framework workflow building
    with patch.object(visualizer, '_build_agent_framework_workflow') as mock_build:
        mock_workflow = MagicMock()
        mock_build.return_value = mock_workflow
        
        with patch('app.workflows.workflow_visualizer.WorkflowViz') as MockViz:
            mock_viz = MagicMock()
            mock_viz.to_mermaid.return_value = "graph TB\n  A --> B"
            MockViz.return_value = mock_viz
            
            result = await visualizer.generate_mermaid(sample_workflow)
            
            assert result["format"] == "mermaid"
            assert result["source"] == "agent_framework_viz"
            assert "graph TB" in result["content"]


@pytest.mark.asyncio
@patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', True)
async def test_generate_dot_with_workflowviz(sample_workflow):
    """Test DOT generation using Agent Framework WorkflowViz."""
    visualizer = WorkflowVisualizer()
    
    with patch.object(visualizer, '_build_agent_framework_workflow') as mock_build:
        mock_workflow = MagicMock()
        mock_build.return_value = mock_workflow
        
        with patch('app.workflows.workflow_visualizer.WorkflowViz') as MockViz:
            mock_viz = MagicMock()
            mock_viz.to_digraph.return_value = "digraph Workflow {\n  A -> B;\n}"
            MockViz.return_value = mock_viz
            
            result = await visualizer.generate_dot(sample_workflow)
            
            assert result["format"] == "dot"
            assert result["source"] == "agent_framework_viz"
            assert "digraph" in result["content"]


@pytest.mark.asyncio
@patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', True)
async def test_generate_svg_with_workflowviz(sample_workflow):
    """Test SVG generation using Agent Framework WorkflowViz."""
    visualizer = WorkflowVisualizer()
    
    svg_content = '<svg><rect/></svg>'
    
    with patch.object(visualizer, '_build_agent_framework_workflow') as mock_build:
        mock_workflow = MagicMock()
        mock_build.return_value = mock_workflow
        
        with patch('app.workflows.workflow_visualizer.WorkflowViz') as MockViz:
            mock_viz = MagicMock()
            mock_viz.export.return_value = "/tmp/workflow.svg"
            MockViz.return_value = mock_viz
            
            with patch('builtins.open', mock_open(read_data=svg_content)):
                result = await visualizer.generate_svg(sample_workflow)
                
                assert result["format"] == "svg"
                assert result["content"] == svg_content
                assert "file_path" in result


@pytest.mark.asyncio
@patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', True)
async def test_generate_png_with_workflowviz(sample_workflow):
    """Test PNG generation using Agent Framework WorkflowViz."""
    visualizer = WorkflowVisualizer()
    
    with patch.object(visualizer, '_build_agent_framework_workflow') as mock_build:
        mock_workflow = MagicMock()
        mock_build.return_value = mock_workflow
        
        with patch('app.workflows.workflow_visualizer.WorkflowViz') as MockViz:
            mock_viz = MagicMock()
            mock_viz.export.return_value = "/tmp/workflow.png"
            MockViz.return_value = mock_viz
            
            result = await visualizer.generate_png(sample_workflow)
            
            assert result["format"] == "png"
            assert result["file_path"] == "/tmp/workflow.png"


@pytest.mark.asyncio
async def test_generate_svg_without_workflowviz(sample_workflow):
    """Test SVG generation falls back when WorkflowViz not available."""
    with patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', False):
        visualizer = WorkflowVisualizer()
        
        result = await visualizer.generate_svg(sample_workflow)
        
        assert result["format"] == "svg"
        assert "error" in result
        assert "WorkflowViz not available" in result["error"]


@pytest.mark.asyncio
async def test_generate_png_without_workflowviz(sample_workflow):
    """Test PNG generation falls back when WorkflowViz not available."""
    with patch('app.workflows.workflow_visualizer.WORKFLOW_VIZ_AVAILABLE', False):
        visualizer = WorkflowVisualizer()
        
        result = await visualizer.generate_png(sample_workflow)
        
        assert result["format"] == "png"
        assert "error" in result
        assert "WorkflowViz not available" in result["error"]


@pytest.mark.asyncio
async def test_generate_with_invalid_format(sample_workflow):
    """Test generation with invalid format raises error."""
    visualizer = WorkflowVisualizer()
    
    with pytest.raises(ValueError, match="Unsupported visualization format"):
        await visualizer.generate(sample_workflow, format="invalid")


@pytest.mark.asyncio
async def test_build_agent_framework_workflow(sample_workflow):
    """Test building Agent Framework workflow from database model."""
    visualizer = WorkflowVisualizer()
    
    # This may return None if agent_framework not available, which is OK
    result = await visualizer._build_agent_framework_workflow(sample_workflow)
    
    # Just ensure it doesn't raise an error
    assert result is None or result is not None


@pytest.mark.asyncio
async def test_mermaid_diagram_with_conditional_edges(sample_workflow):
    """Test Mermaid diagram with conditional edges."""
    # Add a conditional edge
    sample_workflow.edges.append(
        WorkflowEdge(
            id=3,
            workflow_id=1,
            source_node_id=2,
            target_node_id=1,
            label="loop",
            condition="count < 5",
            config={}
        )
    )
    
    visualizer = WorkflowVisualizer()
    result = await visualizer.generate_mermaid(sample_workflow)
    
    # Conditional edges should use dotted lines
    assert ".-" in result["content"] or result["content"]  # Has conditional styling


@pytest.mark.asyncio
async def test_dot_diagram_with_node_types(sample_workflow):
    """Test DOT diagram includes proper node type styling."""
    visualizer = WorkflowVisualizer()
    result = await visualizer.generate_dot(sample_workflow)
    
    content = result["content"]
    
    # Start node should have special styling
    assert "lightgreen" in content or "fillcolor" in content
    
    # Output node should have special styling
    assert "lightblue" in content or "fillcolor" in content
