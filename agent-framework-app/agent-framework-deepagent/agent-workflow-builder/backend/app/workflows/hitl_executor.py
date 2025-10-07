"""
Human-in-the-Loop executor for workflow approval points.

This module provides RequestInfoExecutor pattern for human approvals in workflows,
compatible with Microsoft Agent Framework's HITL patterns.
"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from sqlmodel import Session, select

from app.core.logging import get_logger
from app.models import HumanApprovalRequest, ApprovalStatus

logger = get_logger(__name__)


class RequestType(str, Enum):
    """Types of human approval requests."""
    FUNCTION_APPROVAL = "function_approval"
    DATA_REVIEW = "data_review"
    DECISION_POINT = "decision_point"
    CUSTOM = "custom"


class RequestInfoExecutor:
    """Executor that pauses workflow for human input.
    
    Compatible with Agent Framework's HITL patterns:
    - Pause workflow execution at critical points
    - Emit approval request via WebSocket for real-time notifications
    - Wait for human response with configurable timeout
    - Resume workflow with approved/rejected action
    
    Usage:
        executor = RequestInfoExecutor("executor-1", db_session)
        
        # Request approval
        response = await executor.request_approval(
            workflow_id="workflow-123",
            request_type=RequestType.FUNCTION_APPROVAL,
            data={"function": "delete_data", "params": {...}}
        )
        
        if response["approved"]:
            # Proceed with approved action
            pass
    """
    
    def __init__(self, executor_id: str, db: Session):
        """Initialize HITL executor.
        
        Args:
            executor_id: Unique executor identifier
            db: Database session for persistence
        """
        self.id = executor_id
        self.db = db
        self.pending_requests: Dict[int, HumanApprovalRequest] = {}
    
    async def request_approval(
        self,
        workflow_id: str,
        request_type: RequestType,
        data: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Request human approval and wait for response.
        
        This method:
        1. Creates an approval request in the database
        2. Emits a WebSocket notification to connected clients
        3. Waits for human response with optional timeout
        4. Returns the approval decision and any modifications
        
        Args:
            workflow_id: Workflow requesting approval
            request_type: Type of approval needed (function, data review, etc.)
            data: Request data (function call details, decision options, etc.)
            timeout_seconds: Optional timeout in seconds (default: 3600 = 1 hour)
            
        Returns:
            Dict containing:
                - approved (bool): Whether the request was approved
                - feedback (str): Optional human feedback
                - modified_data (dict): Optional modified parameters
                - responded_at (str): Response timestamp
                
        Raises:
            TimeoutError: If no response received within timeout
        """
        # Create approval request
        request = HumanApprovalRequest(
            workflow_id=workflow_id,
            request_type=request_type.value,
            request_data=data,
            status=ApprovalStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        self.pending_requests[request.id] = request
        
        logger.info(f"Created approval request {request.id} for workflow {workflow_id}")
        
        # Emit WebSocket event for frontend
        await self._emit_approval_request(request)
        
        # Wait for response (with optional timeout)
        try:
            response = await self._wait_for_response(request.id, timeout_seconds)
            return response
        except TimeoutError:
            # Mark as timed out
            request.status = ApprovalStatus.TIMEOUT
            request.updated_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def submit_approval_response(
        self,
        request_id: int,
        approved: bool,
        feedback: Optional[str] = None,
        modified_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Submit human approval response.
        
        Called when a human provides their approval decision. Updates the
        database and notifies the waiting workflow.
        
        Args:
            request_id: Request identifier
            approved: Whether approved or rejected
            feedback: Optional human feedback/comments
            modified_data: Optional modified parameters (e.g., adjusted function args)
            
        Raises:
            ValueError: If request not found or already processed
        """
        # Get request from database
        query = select(HumanApprovalRequest).where(HumanApprovalRequest.id == request_id)
        result = self.db.exec(query)
        request = result.first()
        
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Request {request_id} already processed with status {request.status}")
        
        # Update request
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.response_data = {
            "approved": approved,
            "feedback": feedback,
            "modified_data": modified_data,
            "responded_at": datetime.utcnow().isoformat()
        }
        request.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Update pending requests cache
        self.pending_requests[request_id] = request
        
        # Notify waiting workflow
        await self._notify_response(request_id, request.response_data)
        
        logger.info(f"Approval request {request_id} {'approved' if approved else 'rejected'}")
    
    async def _emit_approval_request(self, request: HumanApprovalRequest):
        """Emit approval request via WebSocket.
        
        Broadcasts the approval request to all connected WebSocket clients
        so the UI can display it to users.
        """
        try:
            from app.services.websocket_service import manager
            
            await manager.broadcast({
                "type": "approval_request",
                "data": {
                    "request_id": request.id,
                    "workflow_id": request.workflow_id,
                    "request_type": request.request_type,
                    "request_data": request.request_data,
                    "created_at": request.created_at.isoformat()
                }
            })
        except Exception as e:
            logger.warning(f"Failed to emit approval request via WebSocket: {e}")
    
    async def _wait_for_response(
        self, 
        request_id: int, 
        timeout_seconds: Optional[int]
    ) -> Dict[str, Any]:
        """Wait for human response with timeout.
        
        Polls the database for response at regular intervals.
        
        Args:
            request_id: Request to wait for
            timeout_seconds: Maximum wait time in seconds
            
        Returns:
            Response data dict
            
        Raises:
            TimeoutError: If timeout exceeded
        """
        max_wait = timeout_seconds or 3600  # 1 hour default
        check_interval = 1  # Check every second
        elapsed = 0
        
        while elapsed < max_wait:
            # Check database for updated status
            query = select(HumanApprovalRequest).where(HumanApprovalRequest.id == request_id)
            result = self.db.exec(query)
            request = result.first()
            
            if request and request.status != ApprovalStatus.PENDING:
                logger.info(f"Received response for request {request_id}: {request.status}")
                return request.response_data or {}
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        logger.warning(f"Approval request {request_id} timed out after {max_wait} seconds")
        raise TimeoutError(f"Approval request {request_id} timed out")
    
    async def _notify_response(self, request_id: int, response_data: Dict[str, Any]):
        """Notify via WebSocket that response received.
        
        Broadcasts the approval response to all connected clients.
        """
        try:
            from app.services.websocket_service import manager
            
            await manager.broadcast({
                "type": "approval_response",
                "data": {
                    "request_id": request_id,
                    "response": response_data
                }
            })
        except Exception as e:
            logger.warning(f"Failed to notify approval response via WebSocket: {e}")


class ApprovalRequiredAIFunction:
    """Wrapper for AI functions requiring human approval.
    
    Compatible with Agent Framework's function tool patterns. Wraps any async
    function to require human approval before execution.
    
    Usage:
        async def delete_user(user_id: str):
            # Sensitive operation
            pass
        
        executor = RequestInfoExecutor("exec-1", db)
        wrapped_fn = ApprovalRequiredAIFunction(
            delete_user, executor, "workflow-123"
        )
        
        # This will pause and wait for approval
        await wrapped_fn(user_id="user-456")
    """
    
    def __init__(
        self,
        function: Callable,
        executor: RequestInfoExecutor,
        workflow_id: str
    ):
        """Initialize approval-required function wrapper.
        
        Args:
            function: The function to wrap
            executor: HITL executor for handling approvals
            workflow_id: Workflow context identifier
        """
        self.function = function
        self.executor = executor
        self.workflow_id = workflow_id
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
    
    async def __call__(self, *args, **kwargs):
        """Execute function with approval gate.
        
        Requests approval before executing the wrapped function. If approval
        includes modified parameters, those are applied before execution.
        
        Raises:
            PermissionError: If approval is denied
        """
        # Request approval before execution
        approval = await self.executor.request_approval(
            workflow_id=self.workflow_id,
            request_type=RequestType.FUNCTION_APPROVAL,
            data={
                "function_name": self.__name__,
                "args": list(args),
                "kwargs": kwargs
            }
        )
        
        if not approval.get("approved"):
            raise PermissionError(f"Function {self.__name__} not approved")
        
        # Use modified parameters if provided
        modified_data = approval.get("modified_data")
        if modified_data:
            kwargs.update(modified_data)
        
        # Execute approved function
        if asyncio.iscoroutinefunction(self.function):
            result = await self.function(*args, **kwargs)
        else:
            result = self.function(*args, **kwargs)
        
        return result
