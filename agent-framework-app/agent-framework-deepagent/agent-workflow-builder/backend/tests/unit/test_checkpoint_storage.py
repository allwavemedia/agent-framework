"""
Unit tests for checkpoint storage functionality.

Tests database-backed checkpoint storage operations including save, load,
list, and delete operations.
"""
import pytest
from datetime import datetime
from sqlmodel import Session

from app.workflows.checkpoint_storage import DatabaseCheckpointStorage
from app.models import WorkflowCheckpoint


@pytest.mark.asyncio
async def test_save_checkpoint(session: Session):
    """Test saving a checkpoint to database."""
    storage = DatabaseCheckpointStorage(session)
    
    # Save checkpoint
    await storage.save_checkpoint(
        workflow_id="test-workflow-1",
        checkpoint_id="step-1",
        state_data={"agents": {}, "step": 1, "context": {}},
        metadata={"user_id": "test-user", "tags": ["test"]}
    )
    
    # Verify checkpoint was saved
    state = await storage.load_checkpoint("test-workflow-1", "step-1")
    assert state is not None
    assert state["step"] == 1
    assert "agents" in state


@pytest.mark.asyncio
async def test_load_checkpoint_specific(session: Session):
    """Test loading a specific checkpoint by ID."""
    storage = DatabaseCheckpointStorage(session)
    
    # Save checkpoint
    test_state = {
        "agents": {"agent1": "state1"},
        "step": 5,
        "context": {"var1": "value1"}
    }
    await storage.save_checkpoint(
        workflow_id="test-workflow-2",
        checkpoint_id="step-5",
        state_data=test_state
    )
    
    # Load checkpoint
    loaded_state = await storage.load_checkpoint("test-workflow-2", "step-5")
    assert loaded_state is not None
    assert loaded_state["step"] == 5
    assert loaded_state["agents"]["agent1"] == "state1"
    assert loaded_state["context"]["var1"] == "value1"


@pytest.mark.asyncio
async def test_load_checkpoint_latest(session: Session):
    """Test loading the latest checkpoint when no ID specified."""
    storage = DatabaseCheckpointStorage(session)
    
    # Save multiple checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id="test-workflow-3",
            checkpoint_id=f"step-{i}",
            state_data={"step": i}
        )
    
    # Load latest checkpoint (should be step-2)
    state = await storage.load_checkpoint("test-workflow-3")
    assert state is not None
    assert state["step"] == 2  # Latest one


@pytest.mark.asyncio
async def test_load_checkpoint_not_found(session: Session):
    """Test loading a non-existent checkpoint."""
    storage = DatabaseCheckpointStorage(session)
    
    # Try to load non-existent checkpoint
    state = await storage.load_checkpoint("non-existent-workflow", "step-1")
    assert state is None


@pytest.mark.asyncio
async def test_list_checkpoints(session: Session):
    """Test listing all checkpoints for a workflow."""
    storage = DatabaseCheckpointStorage(session)
    
    # Create multiple checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id="test-workflow-4",
            checkpoint_id=f"step-{i}",
            state_data={"step": i},
            metadata={"iteration": i}
        )
    
    # List checkpoints
    checkpoints = await storage.list_checkpoints("test-workflow-4")
    assert len(checkpoints) == 3
    
    # Verify checkpoint structure
    for cp in checkpoints:
        assert "checkpoint_id" in cp
        assert "created_at" in cp
        assert "metadata" in cp
    
    # Verify they're in descending order (latest first)
    assert checkpoints[0]["checkpoint_id"] == "step-2"
    assert checkpoints[1]["checkpoint_id"] == "step-1"
    assert checkpoints[2]["checkpoint_id"] == "step-0"


@pytest.mark.asyncio
async def test_list_checkpoints_empty(session: Session):
    """Test listing checkpoints for a workflow with no checkpoints."""
    storage = DatabaseCheckpointStorage(session)
    
    checkpoints = await storage.list_checkpoints("empty-workflow")
    assert checkpoints == []


@pytest.mark.asyncio
async def test_delete_checkpoint(session: Session):
    """Test deleting a specific checkpoint."""
    storage = DatabaseCheckpointStorage(session)
    
    # Save checkpoint
    await storage.save_checkpoint(
        workflow_id="test-workflow-5",
        checkpoint_id="step-to-delete",
        state_data={"step": 1}
    )
    
    # Verify it exists
    state = await storage.load_checkpoint("test-workflow-5", "step-to-delete")
    assert state is not None
    
    # Delete checkpoint
    deleted = await storage.delete_checkpoint("test-workflow-5", "step-to-delete")
    assert deleted is True
    
    # Verify it's gone
    state = await storage.load_checkpoint("test-workflow-5", "step-to-delete")
    assert state is None


@pytest.mark.asyncio
async def test_delete_checkpoint_not_found(session: Session):
    """Test deleting a non-existent checkpoint."""
    storage = DatabaseCheckpointStorage(session)
    
    # Try to delete non-existent checkpoint
    deleted = await storage.delete_checkpoint("test-workflow-6", "non-existent")
    assert deleted is False


@pytest.mark.asyncio
async def test_checkpoint_metadata_preservation(session: Session):
    """Test that metadata is preserved correctly."""
    storage = DatabaseCheckpointStorage(session)
    
    metadata = {
        "user_id": "test-user-123",
        "tags": ["production", "important"],
        "comment": "Critical checkpoint before deployment"
    }
    
    await storage.save_checkpoint(
        workflow_id="test-workflow-7",
        checkpoint_id="metadata-test",
        state_data={"step": 1},
        metadata=metadata
    )
    
    # List and verify metadata
    checkpoints = await storage.list_checkpoints("test-workflow-7")
    assert len(checkpoints) == 1
    assert checkpoints[0]["metadata"]["user_id"] == "test-user-123"
    assert "production" in checkpoints[0]["metadata"]["tags"]


@pytest.mark.asyncio
async def test_multiple_workflows_isolation(session: Session):
    """Test that checkpoints for different workflows are isolated."""
    storage = DatabaseCheckpointStorage(session)
    
    # Save checkpoints for different workflows
    await storage.save_checkpoint(
        workflow_id="workflow-a",
        checkpoint_id="step-1",
        state_data={"workflow": "a"}
    )
    
    await storage.save_checkpoint(
        workflow_id="workflow-b",
        checkpoint_id="step-1",
        state_data={"workflow": "b"}
    )
    
    # Verify isolation
    state_a = await storage.load_checkpoint("workflow-a", "step-1")
    state_b = await storage.load_checkpoint("workflow-b", "step-1")
    
    assert state_a["workflow"] == "a"
    assert state_b["workflow"] == "b"
    
    # Verify list isolation
    checkpoints_a = await storage.list_checkpoints("workflow-a")
    checkpoints_b = await storage.list_checkpoints("workflow-b")
    
    assert len(checkpoints_a) == 1
    assert len(checkpoints_b) == 1
    assert checkpoints_a[0]["checkpoint_id"] == "step-1"
    assert checkpoints_b[0]["checkpoint_id"] == "step-1"
