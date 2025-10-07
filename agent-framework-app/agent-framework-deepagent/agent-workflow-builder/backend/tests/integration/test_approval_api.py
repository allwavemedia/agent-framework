"""
Integration tests for Human-in-the-Loop approval API endpoints.

Tests the complete approval workflow through HTTP endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime

from app.models import HumanApprovalRequest, ApprovalStatus


@pytest.mark.asyncio
async def test_get_pending_approvals_empty(client: TestClient):
    """Test getting pending approvals when none exist."""
    response = client.get("/api/v1/approvals/pending")
    
    assert response.status_code == 200
    approvals = response.json()
    assert approvals == []


@pytest.mark.asyncio
async def test_get_pending_approvals(client: TestClient, session: Session):
    """Test getting pending approval requests."""
    # Create pending requests
    for i in range(3):
        request = HumanApprovalRequest(
            workflow_id=f"workflow-{i}",
            request_type="function_approval",
            request_data={"function": f"func_{i}"},
            status=ApprovalStatus.PENDING,
            created_at=datetime.utcnow()
        )
        session.add(request)
    
    # Create non-pending request (should not appear)
    approved_request = HumanApprovalRequest(
        workflow_id="workflow-approved",
        request_type="function_approval",
        request_data={"function": "approved_func"},
        status=ApprovalStatus.APPROVED,
        created_at=datetime.utcnow()
    )
    session.add(approved_request)
    session.commit()
    
    # Get pending approvals
    response = client.get("/api/v1/approvals/pending")
    
    assert response.status_code == 200
    approvals = response.json()
    assert len(approvals) == 3
    
    # Verify all are pending
    for approval in approvals:
        assert approval["status"] == "pending"
        assert "id" in approval
        assert "workflow_id" in approval
        assert "request_data" in approval


@pytest.mark.asyncio
async def test_get_workflow_approvals(client: TestClient, session: Session):
    """Test getting approvals for a specific workflow."""
    workflow_id = "test-workflow-1"
    
    # Create approvals for target workflow
    for i in range(2):
        request = HumanApprovalRequest(
            workflow_id=workflow_id,
            request_type="data_review",
            request_data={"item": i},
            status=ApprovalStatus.PENDING,
            created_at=datetime.utcnow()
        )
        session.add(request)
    
    # Create approval for different workflow (should not appear)
    other_request = HumanApprovalRequest(
        workflow_id="other-workflow",
        request_type="function_approval",
        request_data={"test": "data"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(other_request)
    session.commit()
    
    # Get approvals for specific workflow
    response = client.get(f"/api/v1/approvals/{workflow_id}")
    
    assert response.status_code == 200
    approvals = response.json()
    assert len(approvals) == 2
    
    # Verify all belong to target workflow
    for approval in approvals:
        assert approval["workflow_id"] == workflow_id


@pytest.mark.asyncio
async def test_get_workflow_approvals_with_status_filter(client: TestClient, session: Session):
    """Test filtering workflow approvals by status."""
    workflow_id = "test-workflow-2"
    
    # Create approvals with different statuses
    pending = HumanApprovalRequest(
        workflow_id=workflow_id,
        request_type="function_approval",
        request_data={"test": 1},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    approved = HumanApprovalRequest(
        workflow_id=workflow_id,
        request_type="function_approval",
        request_data={"test": 2},
        status=ApprovalStatus.APPROVED,
        created_at=datetime.utcnow()
    )
    rejected = HumanApprovalRequest(
        workflow_id=workflow_id,
        request_type="function_approval",
        request_data={"test": 3},
        status=ApprovalStatus.REJECTED,
        created_at=datetime.utcnow()
    )
    session.add_all([pending, approved, rejected])
    session.commit()
    
    # Filter by pending
    response = client.get(f"/api/v1/approvals/{workflow_id}?status=pending")
    assert response.status_code == 200
    approvals = response.json()
    assert len(approvals) == 1
    assert approvals[0]["status"] == "pending"
    
    # Filter by approved
    response = client.get(f"/api/v1/approvals/{workflow_id}?status=approved")
    assert response.status_code == 200
    approvals = response.json()
    assert len(approvals) == 1
    assert approvals[0]["status"] == "approved"


@pytest.mark.asyncio
async def test_get_approval_request_by_id(client: TestClient, session: Session):
    """Test getting a specific approval request by ID."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-3",
        request_type="decision_point",
        request_data={"options": ["A", "B", "C"]},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Get specific request
    response = client.get(f"/api/v1/approvals/request/{request.id}")
    
    assert response.status_code == 200
    approval = response.json()
    assert approval["id"] == request.id
    assert approval["workflow_id"] == "test-workflow-3"
    assert approval["request_type"] == "decision_point"
    assert "options" in approval["request_data"]


@pytest.mark.asyncio
async def test_get_approval_request_not_found(client: TestClient):
    """Test getting non-existent approval request."""
    response = client.get("/api/v1/approvals/request/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_respond_to_approval_approve(client: TestClient, session: Session):
    """Test approving an approval request."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-4",
        request_type="function_approval",
        request_data={"function": "delete_item"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Submit approval
    response = client.post(
        f"/api/v1/approvals/{request.id}/respond",
        json={
            "approved": True,
            "feedback": "Approved for execution"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "processed"
    assert result["approved"] is True
    assert result["request_id"] == request.id
    
    # Verify in database
    session.refresh(request)
    assert request.status == ApprovalStatus.APPROVED
    assert request.response_data["approved"] is True
    assert request.response_data["feedback"] == "Approved for execution"


@pytest.mark.asyncio
async def test_respond_to_approval_reject(client: TestClient, session: Session):
    """Test rejecting an approval request."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-5",
        request_type="data_review",
        request_data={"data": "sensitive"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Submit rejection
    response = client.post(
        f"/api/v1/approvals/{request.id}/respond",
        json={
            "approved": False,
            "feedback": "Data needs review"
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["approved"] is False
    
    # Verify in database
    session.refresh(request)
    assert request.status == ApprovalStatus.REJECTED


@pytest.mark.asyncio
async def test_respond_with_modified_data(client: TestClient, session: Session):
    """Test responding with modified parameters."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-6",
        request_type="function_approval",
        request_data={"timeout": 30},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Approve with modifications
    response = client.post(
        f"/api/v1/approvals/{request.id}/respond",
        json={
            "approved": True,
            "modified_data": {"timeout": 60}
        }
    )
    
    assert response.status_code == 200
    
    # Verify modifications saved
    session.refresh(request)
    assert request.response_data["modified_data"]["timeout"] == 60


@pytest.mark.asyncio
async def test_respond_to_already_processed(client: TestClient, session: Session):
    """Test responding to already processed request."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-7",
        request_type="function_approval",
        request_data={"test": "data"},
        status=ApprovalStatus.APPROVED,  # Already processed
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Try to process again
    response = client.post(
        f"/api/v1/approvals/{request.id}/respond",
        json={"approved": False}
    )
    
    assert response.status_code == 400
    assert "already processed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_approval_request(client: TestClient, session: Session):
    """Test cancelling a pending approval request."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-8",
        request_type="custom",
        request_data={"test": "cancel"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Cancel request
    response = client.delete(f"/api/v1/approvals/{request.id}")
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "cancelled"
    assert result["approved"] is False
    
    # Verify cancelled in database
    session.refresh(request)
    assert request.status == ApprovalStatus.REJECTED


@pytest.mark.asyncio
async def test_cancel_already_processed(client: TestClient, session: Session):
    """Test cancelling already processed request."""
    request = HumanApprovalRequest(
        workflow_id="test-workflow-9",
        request_type="function_approval",
        request_data={"test": "data"},
        status=ApprovalStatus.APPROVED,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Try to cancel
    response = client.delete(f"/api/v1/approvals/{request.id}")
    
    assert response.status_code == 400
    assert "cannot cancel" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_approval_workflow_lifecycle(client: TestClient, session: Session):
    """Test complete approval lifecycle."""
    workflow_id = "lifecycle-test"
    
    # Step 1: Create approval request
    request = HumanApprovalRequest(
        workflow_id=workflow_id,
        request_type="function_approval",
        request_data={"function": "critical_operation"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Step 2: Check it appears in pending
    response = client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    pending = response.json()
    assert any(a["id"] == request.id for a in pending)
    
    # Step 3: Get specific request
    response = client.get(f"/api/v1/approvals/request/{request.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    
    # Step 4: Approve it
    response = client.post(
        f"/api/v1/approvals/{request.id}/respond",
        json={"approved": True, "feedback": "OK to proceed"}
    )
    assert response.status_code == 200
    
    # Step 5: Verify no longer in pending
    response = client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    pending = response.json()
    assert not any(a["id"] == request.id for a in pending)
    
    # Step 6: Verify in workflow approvals with approved status
    response = client.get(f"/api/v1/approvals/{workflow_id}?status=approved")
    assert response.status_code == 200
    approved = response.json()
    assert len(approved) == 1
    assert approved[0]["id"] == request.id
