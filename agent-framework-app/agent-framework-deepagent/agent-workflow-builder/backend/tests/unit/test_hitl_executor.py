"""
Unit tests for Human-in-the-Loop executor functionality.

Tests RequestInfoExecutor and ApprovalRequiredAIFunction classes.
"""
import pytest
import asyncio
from datetime import datetime
from sqlmodel import Session

from app.workflows.hitl_executor import (
    RequestInfoExecutor,
    RequestType,
    ApprovalRequiredAIFunction
)
from app.models import HumanApprovalRequest, ApprovalStatus


@pytest.mark.asyncio
async def test_create_approval_request(session: Session):
    """Test creating an approval request."""
    executor = RequestInfoExecutor("test-executor-1", session)
    
    # Create approval request in background (will timeout quickly)
    request_task = asyncio.create_task(
        executor.request_approval(
            workflow_id="test-workflow-1",
            request_type=RequestType.FUNCTION_APPROVAL,
            data={"function": "test_func", "args": []},
            timeout_seconds=1
        )
    )
    
    # Give it time to create the request
    await asyncio.sleep(0.5)
    
    # Check database
    requests = session.query(HumanApprovalRequest).all()
    assert len(requests) == 1
    assert requests[0].workflow_id == "test-workflow-1"
    assert requests[0].request_type == RequestType.FUNCTION_APPROVAL.value
    assert requests[0].status == ApprovalStatus.PENDING
    
    # Let it timeout
    with pytest.raises(TimeoutError):
        await request_task


@pytest.mark.asyncio
async def test_submit_approval_response_approved(session: Session):
    """Test submitting an approved response."""
    executor = RequestInfoExecutor("test-executor-2", session)
    
    # Create approval request
    request = HumanApprovalRequest(
        workflow_id="test-workflow-2",
        request_type=RequestType.DATA_REVIEW.value,
        request_data={"data": "test"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Submit approval
    await executor.submit_approval_response(
        request_id=request.id,
        approved=True,
        feedback="Looks good"
    )
    
    # Verify
    session.refresh(request)
    assert request.status == ApprovalStatus.APPROVED
    assert request.response_data["approved"] is True
    assert request.response_data["feedback"] == "Looks good"
    assert request.updated_at is not None


@pytest.mark.asyncio
async def test_submit_approval_response_rejected(session: Session):
    """Test submitting a rejected response."""
    executor = RequestInfoExecutor("test-executor-3", session)
    
    # Create approval request
    request = HumanApprovalRequest(
        workflow_id="test-workflow-3",
        request_type=RequestType.DECISION_POINT.value,
        request_data={"options": ["A", "B"]},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Submit rejection
    await executor.submit_approval_response(
        request_id=request.id,
        approved=False,
        feedback="Not ready yet"
    )
    
    # Verify
    session.refresh(request)
    assert request.status == ApprovalStatus.REJECTED
    assert request.response_data["approved"] is False
    assert request.response_data["feedback"] == "Not ready yet"


@pytest.mark.asyncio
async def test_submit_approval_with_modified_data(session: Session):
    """Test submitting approval with modified parameters."""
    executor = RequestInfoExecutor("test-executor-4", session)
    
    # Create approval request
    request = HumanApprovalRequest(
        workflow_id="test-workflow-4",
        request_type=RequestType.FUNCTION_APPROVAL.value,
        request_data={"function": "send_email", "to": "user@example.com"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Submit with modifications
    await executor.submit_approval_response(
        request_id=request.id,
        approved=True,
        modified_data={"to": "admin@example.com"}
    )
    
    # Verify
    session.refresh(request)
    assert request.status == ApprovalStatus.APPROVED
    assert request.response_data["modified_data"]["to"] == "admin@example.com"


@pytest.mark.asyncio
async def test_submit_approval_invalid_request(session: Session):
    """Test submitting approval for non-existent request."""
    executor = RequestInfoExecutor("test-executor-5", session)
    
    with pytest.raises(ValueError, match="Request 99999 not found"):
        await executor.submit_approval_response(
            request_id=99999,
            approved=True
        )


@pytest.mark.asyncio
async def test_submit_approval_already_processed(session: Session):
    """Test submitting approval for already processed request."""
    executor = RequestInfoExecutor("test-executor-6", session)
    
    # Create already approved request
    request = HumanApprovalRequest(
        workflow_id="test-workflow-6",
        request_type=RequestType.CUSTOM.value,
        request_data={"test": "data"},
        status=ApprovalStatus.APPROVED,  # Already approved
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Try to process again
    with pytest.raises(ValueError, match="already processed"):
        await executor.submit_approval_response(
            request_id=request.id,
            approved=False
        )


@pytest.mark.asyncio
async def test_approval_required_function_approved():
    """Test ApprovalRequiredAIFunction with approved request."""
    
    # Mock function
    async def test_function(x: int, y: int) -> int:
        return x + y
    
    # Mock executor with auto-approve
    class MockExecutor:
        async def request_approval(self, **kwargs):
            return {"approved": True, "modified_data": None}
    
    wrapped = ApprovalRequiredAIFunction(
        test_function,
        MockExecutor(),
        "test-workflow"
    )
    
    result = await wrapped(5, 10)
    assert result == 15


@pytest.mark.asyncio
async def test_approval_required_function_rejected():
    """Test ApprovalRequiredAIFunction with rejected request."""
    
    # Mock function
    async def test_function(x: int) -> int:
        return x * 2
    
    # Mock executor with auto-reject
    class MockExecutor:
        async def request_approval(self, **kwargs):
            return {"approved": False}
    
    wrapped = ApprovalRequiredAIFunction(
        test_function,
        MockExecutor(),
        "test-workflow"
    )
    
    with pytest.raises(PermissionError, match="not approved"):
        await wrapped(5)


@pytest.mark.asyncio
async def test_approval_required_function_with_modifications():
    """Test ApprovalRequiredAIFunction with parameter modifications."""
    
    # Mock function
    async def test_function(message: str, count: int = 1) -> str:
        return message * count
    
    # Mock executor that modifies parameters
    class MockExecutor:
        async def request_approval(self, **kwargs):
            return {
                "approved": True,
                "modified_data": {"count": 3}  # Override count
            }
    
    wrapped = ApprovalRequiredAIFunction(
        test_function,
        MockExecutor(),
        "test-workflow"
    )
    
    result = await wrapped(message="Hi", count=1)
    assert result == "HiHiHi"  # count was modified to 3


@pytest.mark.asyncio
async def test_request_types():
    """Test all request type enum values."""
    assert RequestType.FUNCTION_APPROVAL.value == "function_approval"
    assert RequestType.DATA_REVIEW.value == "data_review"
    assert RequestType.DECISION_POINT.value == "decision_point"
    assert RequestType.CUSTOM.value == "custom"


@pytest.mark.asyncio
async def test_pending_requests_cache(session: Session):
    """Test that pending requests are cached correctly."""
    executor = RequestInfoExecutor("test-executor-7", session)
    
    # Create request
    request = HumanApprovalRequest(
        workflow_id="test-workflow-7",
        request_type=RequestType.FUNCTION_APPROVAL.value,
        request_data={"test": "data"},
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    
    # Manually add to cache (simulating request_approval flow)
    executor.pending_requests[request.id] = request
    
    # Submit response
    await executor.submit_approval_response(
        request_id=request.id,
        approved=True
    )
    
    # Verify cache was updated
    assert request.id in executor.pending_requests
    assert executor.pending_requests[request.id].status == ApprovalStatus.APPROVED
