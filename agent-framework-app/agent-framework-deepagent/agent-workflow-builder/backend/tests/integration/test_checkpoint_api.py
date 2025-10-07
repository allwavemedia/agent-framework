"""
Integration tests for checkpoint API endpoints.

Tests the complete checkpoint API functionality including listing, restoring,
and deleting checkpoints through HTTP endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.workflows.checkpoint_storage import DatabaseCheckpointStorage


@pytest.mark.asyncio
async def test_list_checkpoints_endpoint(client: TestClient, session: Session):
    """Test listing checkpoints via API endpoint."""
    storage = DatabaseCheckpointStorage(session)
    
    # Create test checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id="api-test-workflow-1",
            checkpoint_id=f"step-{i}",
            state_data={"step": i},
            metadata={"iteration": i}
        )
    
    # Call API endpoint
    response = client.get("/api/v1/checkpoints/api-test-workflow-1")
    
    assert response.status_code == 200
    checkpoints = response.json()
    assert len(checkpoints) == 3
    
    # Verify structure
    for cp in checkpoints:
        assert "checkpoint_id" in cp
        assert "created_at" in cp
        assert "metadata" in cp


@pytest.mark.asyncio
async def test_list_checkpoints_empty_endpoint(client: TestClient):
    """Test listing checkpoints for workflow with no checkpoints."""
    response = client.get("/api/v1/checkpoints/empty-workflow")
    
    assert response.status_code == 200
    checkpoints = response.json()
    assert checkpoints == []


@pytest.mark.asyncio
async def test_restore_checkpoint_specific(client: TestClient, session: Session):
    """Test restoring a specific checkpoint via API."""
    storage = DatabaseCheckpointStorage(session)
    
    # Create checkpoint
    await storage.save_checkpoint(
        workflow_id="api-test-workflow-2",
        checkpoint_id="step-5",
        state_data={"step": 5, "data": "important"}
    )
    
    # Restore via API
    response = client.post(
        "/api/v1/checkpoints/api-test-workflow-2/restore",
        json={"checkpoint_id": "step-5"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "restored"
    assert result["workflow_id"] == "api-test-workflow-2"
    assert result["checkpoint_id"] == "step-5"


@pytest.mark.asyncio
async def test_restore_checkpoint_latest(client: TestClient, session: Session):
    """Test restoring latest checkpoint via API."""
    storage = DatabaseCheckpointStorage(session)
    
    # Create multiple checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id="api-test-workflow-3",
            checkpoint_id=f"step-{i}",
            state_data={"step": i}
        )
    
    # Restore latest (no checkpoint_id specified)
    response = client.post(
        "/api/v1/checkpoints/api-test-workflow-3/restore",
        json={}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "restored"
    assert result["workflow_id"] == "api-test-workflow-3"


@pytest.mark.asyncio
async def test_restore_checkpoint_not_found(client: TestClient):
    """Test restoring a non-existent checkpoint."""
    response = client.post(
        "/api/v1/checkpoints/non-existent-workflow/restore",
        json={"checkpoint_id": "step-1"}
    )
    
    assert response.status_code == 404
    result = response.json()
    # Check for either "not found" or "no checkpoint found" in the detail message
    assert "not found" in result["detail"].lower() or "no checkpoint" in result["detail"].lower()


@pytest.mark.asyncio
async def test_delete_checkpoint_endpoint(client: TestClient, session: Session):
    """Test deleting a checkpoint via API."""
    storage = DatabaseCheckpointStorage(session)
    
    # Create checkpoint
    await storage.save_checkpoint(
        workflow_id="api-test-workflow-4",
        checkpoint_id="step-to-delete",
        state_data={"step": 1}
    )
    
    # Delete via API
    response = client.delete("/api/v1/checkpoints/api-test-workflow-4/step-to-delete")
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "deleted"
    assert result["checkpoint_id"] == "step-to-delete"
    
    # Verify it's actually deleted
    checkpoints = await storage.list_checkpoints("api-test-workflow-4")
    assert len(checkpoints) == 0


@pytest.mark.asyncio
async def test_delete_checkpoint_not_found(client: TestClient):
    """Test deleting a non-existent checkpoint."""
    response = client.delete("/api/v1/checkpoints/api-test-workflow-5/non-existent")
    
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


@pytest.mark.asyncio
async def test_checkpoint_workflow_lifecycle(client: TestClient, session: Session):
    """Test complete checkpoint lifecycle: create, list, restore, delete."""
    storage = DatabaseCheckpointStorage(session)
    workflow_id = "api-test-lifecycle"
    
    # Step 1: Create checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id=workflow_id,
            checkpoint_id=f"step-{i}",
            state_data={"step": i},
            metadata={"iteration": i}
        )
    
    # Step 2: List checkpoints
    response = client.get(f"/api/v1/checkpoints/{workflow_id}")
    assert response.status_code == 200
    checkpoints = response.json()
    assert len(checkpoints) == 3
    
    # Step 3: Restore specific checkpoint
    response = client.post(
        f"/api/v1/checkpoints/{workflow_id}/restore",
        json={"checkpoint_id": "step-1"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "restored"
    
    # Step 4: Delete a checkpoint
    response = client.delete(f"/api/v1/checkpoints/{workflow_id}/step-0")
    assert response.status_code == 200
    
    # Step 5: Verify deletion
    response = client.get(f"/api/v1/checkpoints/{workflow_id}")
    assert response.status_code == 200
    checkpoints = response.json()
    assert len(checkpoints) == 2  # One deleted
    assert all(cp["checkpoint_id"] != "step-0" for cp in checkpoints)


@pytest.mark.asyncio
async def test_checkpoint_metadata_via_api(client: TestClient, session: Session):
    """Test that metadata is correctly returned via API."""
    storage = DatabaseCheckpointStorage(session)
    
    metadata = {
        "user": "test-user",
        "tags": ["important", "production"],
        "comment": "Pre-deployment checkpoint"
    }
    
    await storage.save_checkpoint(
        workflow_id="api-test-metadata",
        checkpoint_id="step-1",
        state_data={"step": 1},
        metadata=metadata
    )
    
    # Retrieve via API
    response = client.get("/api/v1/checkpoints/api-test-metadata")
    assert response.status_code == 200
    
    checkpoints = response.json()
    assert len(checkpoints) == 1
    assert checkpoints[0]["metadata"]["user"] == "test-user"
    assert "important" in checkpoints[0]["metadata"]["tags"]
