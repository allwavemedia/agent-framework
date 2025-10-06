"""Tests for Agent API endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestAgentEndpoints:
    """Test suite for agent API endpoints."""
    
    def test_list_agents_empty(self, client: TestClient):
        """Test listing agents when database is empty."""
        response = client.get("/api/agents/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_agent(self, client: TestClient):
        """Test creating a new agent."""
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are a helpful assistant.",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "tools": [],
            "config": {}
        }
        
        response = client.post("/api/agents/", json=agent_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["description"] == agent_data["description"]
        assert data["agent_type"] == agent_data["agent_type"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_agent(self, client: TestClient):
        """Test getting a specific agent by ID."""
        # First create an agent
        agent_data = {
            "name": "Get Test Agent",
            "description": "Agent for get test",
            "agent_type": "CHAT_AGENT",
            "instructions": "You are helpful.",
            "model": "gpt-4"
        }
        
        create_response = client.post("/api/agents/", json=agent_data)
        agent_id = create_response.json()["id"]
        
        # Now get the agent
        response = client.get(f"/api/agents/{agent_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == agent_data["name"]
    
    def test_get_nonexistent_agent(self, client: TestClient):
        """Test getting an agent that doesn't exist."""
        response = client.get("/api/agents/99999")
        
        assert response.status_code == 404
    
    def test_update_agent(self, client: TestClient):
        """Test updating an agent."""
        # Create an agent
        agent_data = {
            "name": "Original Name",
            "description": "Original description",
            "agent_type": "CHAT_AGENT",
            "instructions": "Original instructions",
            "model": "gpt-4"
        }
        
        create_response = client.post("/api/agents/", json=agent_data)
        agent_id = create_response.json()["id"]
        
        # Update the agent
        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/agents/{agent_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert "updated_at" in data
    
    def test_delete_agent(self, client: TestClient):
        """Test deleting an agent."""
        # Create an agent
        agent_data = {
            "name": "Delete Test Agent",
            "description": "Agent to be deleted",
            "agent_type": "CHAT_AGENT",
            "instructions": "Test",
            "model": "gpt-4"
        }
        
        create_response = client.post("/api/agents/", json=agent_data)
        agent_id = create_response.json()["id"]
        
        # Delete the agent
        response = client.delete(f"/api/agents/{agent_id}")
        
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f"/api/agents/{agent_id}")
        assert get_response.status_code == 404
    
    def test_list_agents_with_data(self, client: TestClient):
        """Test listing agents when database has data."""
        # Create multiple agents
        for i in range(3):
            agent_data = {
                "name": f"Agent {i}",
                "description": f"Description {i}",
                "agent_type": "CHAT_AGENT",
                "instructions": f"Instructions {i}",
                "model": "gpt-4"
            }
            client.post("/api/agents/", json=agent_data)
        
        # List agents
        response = client.get("/api/agents/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in agent for agent in data)
    
    def test_list_agents_with_pagination(self, client: TestClient):
        """Test listing agents with pagination."""
        # Create multiple agents
        for i in range(5):
            agent_data = {
                "name": f"Paged Agent {i}",
                "description": f"Description {i}",
                "agent_type": "CHAT_AGENT",
                "instructions": f"Instructions {i}",
                "model": "gpt-4"
            }
            client.post("/api/agents/", json=agent_data)
        
        # List with pagination
        response = client.get("/api/agents/?skip=0&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
    
    def test_create_agent_missing_required_fields(self, client: TestClient):
        """Test creating an agent with missing required fields."""
        agent_data = {
            "name": "Incomplete Agent"
            # Missing required fields like agent_type, instructions
        }
        
        response = client.post("/api/agents/", json=agent_data)
        
        assert response.status_code == 422  # Validation error
