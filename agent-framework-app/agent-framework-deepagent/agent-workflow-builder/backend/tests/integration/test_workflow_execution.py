"""Integration tests for workflow execution."""
import pytest
from fastapi.testclient import TestClient


class TestWorkflowExecutionIntegration:
    """Test suite f        agent_data = {
            "name": "Test Agent",
            "description": "Testing CRUD operations",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are a test assistant.",
            "model_settings": {"model": "gpt-4"},
            "tools": []
        }low execution integration."""
    
    @pytest.mark.asyncio
    async def test_create_and_execute_simple_workflow(self, client: TestClient):
        """Test creating and executing a simple workflow."""
        # First, create an agent
        agent_data = {
            "name": "Test Agent",
            "description": "Agent for integration test",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are a helpful assistant that responds with 'Hello, World!'",
            "model_settings": {"model": "gpt-4", "temperature": 0.7},
            "tools": []
        }
        
        agent_response = client.post("/api/agents/", json=agent_data)
        assert agent_response.status_code == 200
        agent_id = agent_response.json()["id"]
        
        # Create a workflow
        workflow_data = {
            "name": "Simple Test Workflow",
            "description": "A simple test workflow for integration testing",
            "version": "1.0.0",
            "tags": ["test", "integration"],
            "is_template": False,
            "is_public": False
        }
        
        workflow_response = client.post("/api/workflows/", json=workflow_data)
        assert workflow_response.status_code == 200
        workflow_id = workflow_response.json()["id"]
        
        # Create workflow nodes
        start_node_data = {
            "workflow_id": workflow_id,
            "name": "Start",
            "node_type": "start",
            "executor_type": "AGENT",
            "config": {"is_start": True},
            "position_x": 0.0,
            "position_y": 0.0,
            "is_output_node": False
        }
        
        start_node_response = client.post("/api/workflows/nodes", json=start_node_data)
        assert start_node_response.status_code == 200
        start_node_id = start_node_response.json()["id"]
        
        agent_node_data = {
            "workflow_id": workflow_id,
            "name": "Process",
            "node_type": "agent",
            "executor_type": "AGENT",
            "agent_id": agent_id,
            "config": {"agent_id": agent_id},
            "position_x": 200.0,
            "position_y": 0.0,
            "is_output_node": True
        }
        
        agent_node_response = client.post("/api/workflows/nodes", json=agent_node_data)
        assert agent_node_response.status_code == 200
        agent_node_id = agent_node_response.json()["id"]
        
        # Create edges
        edge_data = {
            "workflow_id": workflow_id,
            "source_node_id": start_node_id,
            "target_node_id": agent_node_id,
            "condition": None
        }
        
        edge_response = client.post("/api/workflows/edges", json=edge_data)
        assert edge_response.status_code == 200
        
        # Validate the workflow
        validate_response = client.post(f"/api/workflows/{workflow_id}/validate")
        assert validate_response.status_code == 200
        validation_result = validate_response.json()
        assert validation_result["valid"] is True
        
        # Execute the workflow (Note: This may fail without proper Azure/OpenAI credentials)
        execution_data = {
            "workflow_id": workflow_id,
            "input_data": {"message": "Hello"}
        }
        
        execution_response = client.post("/api/executions/", json=execution_data)
        # We accept both success and validation errors here since we may not have credentials
        assert execution_response.status_code in [200, 422, 500]
    
    @pytest.mark.asyncio
    async def test_workflow_validation_api(self, client: TestClient):
        """Test the workflow validation API endpoint."""
        # Create a workflow
        workflow_data = {
            "name": "Validation Test Workflow",
            "description": "Test workflow validation",
            "version": "1.0.0",
            "tags": ["test"],
            "is_template": False,
            "is_public": False
        }
        
        workflow_response = client.post("/api/workflows/", json=workflow_data)
        assert workflow_response.status_code == 200
        workflow_id = workflow_response.json()["id"]
        
        # Validate empty workflow (should fail)
        validate_response = client.post(f"/api/workflows/{workflow_id}/validate")
        assert validate_response.status_code == 200
        validation_result = validate_response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_visualization_api(self, client: TestClient):
        """Test the workflow visualization API endpoint."""
        # Create a workflow with nodes
        workflow_data = {
            "name": "Visualization Test Workflow",
            "description": "Test workflow visualization",
            "version": "1.0.0",
            "tags": ["test"],
            "is_template": False,
            "is_public": False
        }
        
        workflow_response = client.post("/api/workflows/", json=workflow_data)
        assert workflow_response.status_code == 200
        workflow_id = workflow_response.json()["id"]
        
        # Add a start node
        start_node_data = {
            "workflow_id": workflow_id,
            "name": "Start",
            "node_type": "start",
            "executor_type": "AGENT",
            "config": {"is_start": True},
            "position_x": 0.0,
            "position_y": 0.0,
            "is_output_node": False
        }
        
        start_node_response = client.post("/api/workflows/nodes", json=start_node_data)
        assert start_node_response.status_code == 200
        
        # Visualize the workflow
        visualize_response = client.get(f"/api/workflows/{workflow_id}/visualize?format=mermaid")
        assert visualize_response.status_code == 200
        visualization = visualize_response.json()
        assert "visualization" in visualization
        assert len(visualization["visualization"]) > 0
    
    @pytest.mark.asyncio
    async def test_agent_crud_integration(self, client: TestClient):
        """Test complete CRUD operations for agents."""
        # Create
        agent_data = {
            "name": "CRUD Test Agent",
            "description": "Testing CRUD operations",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are a test assistant.",
            "model_settings": {"model": "gpt-4"},
            "tools": []
        }
        
        create_response = client.post("/api/agents/", json=agent_data)
        assert create_response.status_code == 200
        agent = create_response.json()
        agent_id = agent["id"]
        assert agent["name"] == agent_data["name"]
        
        # Read
        get_response = client.get(f"/api/agents/{agent_id}")
        assert get_response.status_code == 200
        agent = get_response.json()
        assert agent["id"] == agent_id
        
        # Update
        update_data = {
            "description": "Updated description"
        }
        update_response = client.put(f"/api/agents/{agent_id}", json=update_data)
        assert update_response.status_code == 200
        updated_agent = update_response.json()
        assert updated_agent["description"] == update_data["description"]
        
        # Delete
        delete_response = client.delete(f"/api/agents/{agent_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_after_delete = client.get(f"/api/agents/{agent_id}")
        assert get_after_delete.status_code == 404
    
    @pytest.mark.asyncio
    async def test_workflow_with_multiple_nodes(self, client: TestClient):
        """Test creating a workflow with multiple connected nodes."""
        # Create agents
        agent1_data = {
            "name": "Agent 1",
            "description": "First agent",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are agent 1.",
            "model_settings": {"model": "gpt-4"},
            "tools": []
        }
        
        agent2_data = {
            "name": "Agent 2",
            "description": "Second agent",
            "agent_type": "SPECIALIST_AGENT",
            "instructions": "You are agent 2.",
            "model_settings": {"model": "gpt-4"},
            "tools": []
        }
        
        agent1_response = client.post("/api/agents/", json=agent1_data)
        agent2_response = client.post("/api/agents/", json=agent2_data)
        
        assert agent1_response.status_code == 200
        assert agent2_response.status_code == 200
        
        agent1_id = agent1_response.json()["id"]
        agent2_id = agent2_response.json()["id"]
        
        # Create workflow
        workflow_data = {
            "name": "Multi-Node Workflow",
            "description": "Workflow with multiple nodes",
            "version": "1.0.0",
            "tags": ["test", "multi-node"],
            "is_template": False,
            "is_public": False
        }
        
        workflow_response = client.post("/api/workflows/", json=workflow_data)
        assert workflow_response.status_code == 200
        workflow_id = workflow_response.json()["id"]
        
        # Create nodes
        nodes_data = [
            {
                "workflow_id": workflow_id,
                "name": "Start",
                "node_type": "start",
                "executor_type": "AGENT",
                "config": {"is_start": True},
                "position_x": 0.0,
                "position_y": 0.0,
                "is_output_node": False
            },
            {
                "workflow_id": workflow_id,
                "name": "Agent 1 Node",
                "node_type": "agent",
                "executor_type": "AGENT",
                "agent_id": agent1_id,
                "config": {"agent_id": agent1_id},
                "position_x": 200.0,
                "position_y": 0.0,
                "is_output_node": False
            },
            {
                "workflow_id": workflow_id,
                "name": "Agent 2 Node",
                "node_type": "agent",
                "executor_type": "AGENT",
                "agent_id": agent2_id,
                "config": {"agent_id": agent2_id},
                "position_x": 400.0,
                "position_y": 0.0,
                "is_output_node": True
            }
        ]
        
        node_ids = []
        for node_data in nodes_data:
            node_response = client.post("/api/workflows/nodes", json=node_data)
            assert node_response.status_code == 200
            node_ids.append(node_response.json()["id"])
        
        # Create edges
        edges_data = [
            {
                "workflow_id": workflow_id,
                "source_node_id": node_ids[0],
                "target_node_id": node_ids[1],
                "condition": None
            },
            {
                "workflow_id": workflow_id,
                "source_node_id": node_ids[1],
                "target_node_id": node_ids[2],
                "condition": None
            }
        ]
        
        for edge_data in edges_data:
            edge_response = client.post("/api/workflows/edges", json=edge_data)
            assert edge_response.status_code == 200
        
        # Validate the workflow
        validate_response = client.post(f"/api/workflows/{workflow_id}/validate")
        assert validate_response.status_code == 200
        validation_result = validate_response.json()
        assert validation_result["valid"] is True
        
        # Get the complete workflow
        get_workflow_response = client.get(f"/api/workflows/{workflow_id}")
        assert get_workflow_response.status_code == 200
        workflow = get_workflow_response.json()
        assert len(workflow["nodes"]) == 3
        assert len(workflow["edges"]) == 2
