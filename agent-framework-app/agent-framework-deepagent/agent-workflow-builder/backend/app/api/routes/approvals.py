"""
API routes for human-in-the-loop approval management.

Provides endpoints for listing, responding to, and managing approval requests
in HITL workflows.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.workflows.hitl_executor import RequestInfoExecutor
from app.models import HumanApprovalRequest, ApprovalStatus
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ApprovalResponse(BaseModel):
    """Model for approval response submission."""
    approved: bool
    feedback: Optional[str] = None
    modified_data: Optional[Dict[str, Any]] = None


class ApprovalRequestResponse(BaseModel):
    """Response model for approval request details."""
    id: int
    workflow_id: str
    request_type: str
    request_data: Dict[str, Any]
    status: str
    created_at: str
    updated_at: Optional[str] = None


class ApprovalStatusResponse(BaseModel):
    """Response model for approval operations."""
    status: str
    message: Optional[str] = None
    request_id: Optional[int] = None
    approved: Optional[bool] = None


@router.get("/pending", response_model=List[ApprovalRequestResponse])
async def get_pending_approvals(
    db: Session = Depends(get_db)
) -> List[ApprovalRequestResponse]:
    """Get all pending approval requests.
    
    Returns a list of approval requests awaiting human decision,
    ordered by creation time (newest first).
    
    Args:
        db: Database session
        
    Returns:
        List of pending approval requests
        
    Example:
        GET /api/v1/approvals/pending
    """
    try:
        query = select(HumanApprovalRequest).where(
            HumanApprovalRequest.status == ApprovalStatus.PENDING
        ).order_by(HumanApprovalRequest.created_at.desc())
        
        result = db.exec(query)
        requests = result.all()
        
        return [
            ApprovalRequestResponse(
                id=req.id,
                workflow_id=req.workflow_id,
                request_type=req.request_type,
                request_data=req.request_data,
                status=req.status.value,
                created_at=req.created_at.isoformat(),
                updated_at=req.updated_at.isoformat() if req.updated_at else None
            )
            for req in requests
        ]
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=List[ApprovalRequestResponse])
async def get_workflow_approvals(
    workflow_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[ApprovalRequestResponse]:
    """Get all approval requests for a specific workflow.
    
    Optionally filter by status (pending, approved, rejected, timeout).
    
    Args:
        workflow_id: Workflow identifier
        status: Optional status filter
        db: Database session
        
    Returns:
        List of approval requests for the workflow
        
    Example:
        GET /api/v1/approvals/workflow-123?status=pending
    """
    try:
        query = select(HumanApprovalRequest).where(
            HumanApprovalRequest.workflow_id == workflow_id
        )
        
        if status:
            try:
                status_enum = ApprovalStatus(status)
                query = query.where(HumanApprovalRequest.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Must be one of: pending, approved, rejected, timeout"
                )
        
        query = query.order_by(HumanApprovalRequest.created_at.desc())
        
        result = db.exec(query)
        requests = result.all()
        
        return [
            ApprovalRequestResponse(
                id=req.id,
                workflow_id=req.workflow_id,
                request_type=req.request_type,
                request_data=req.request_data,
                status=req.status.value,
                created_at=req.created_at.isoformat(),
                updated_at=req.updated_at.isoformat() if req.updated_at else None
            )
            for req in requests
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request/{request_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    request_id: int,
    db: Session = Depends(get_db)
) -> ApprovalRequestResponse:
    """Get details of a specific approval request.
    
    Args:
        request_id: Approval request identifier
        db: Database session
        
    Returns:
        Approval request details
        
    Raises:
        HTTPException: If request not found
        
    Example:
        GET /api/v1/approvals/request/123
    """
    try:
        query = select(HumanApprovalRequest).where(
            HumanApprovalRequest.id == request_id
        )
        result = db.exec(query)
        request = result.first()
        
        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Approval request {request_id} not found"
            )
        
        return ApprovalRequestResponse(
            id=request.id,
            workflow_id=request.workflow_id,
            request_type=request.request_type,
            request_data=request.request_data,
            status=request.status.value,
            created_at=request.created_at.isoformat(),
            updated_at=request.updated_at.isoformat() if request.updated_at else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get approval request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/respond", response_model=ApprovalStatusResponse)
async def respond_to_approval(
    request_id: int,
    response: ApprovalResponse,
    db: Session = Depends(get_db)
) -> ApprovalStatusResponse:
    """Submit approval response for a pending request.
    
    Approves or rejects a pending approval request. Optionally includes
    feedback and modified parameters.
    
    Args:
        request_id: Approval request identifier
        response: Approval response with decision and optional data
        db: Database session
        
    Returns:
        Status of the response operation
        
    Raises:
        HTTPException: If request not found or already processed
        
    Example:
        POST /api/v1/approvals/123/respond
        Body: {
            "approved": true,
            "feedback": "Looks good",
            "modified_data": {"timeout": 60}
        }
    """
    try:
        # Get request
        query = select(HumanApprovalRequest).where(
            HumanApprovalRequest.id == request_id
        )
        result = db.exec(query)
        request = result.first()
        
        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Approval request {request_id} not found"
            )
        
        if request.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Request already processed with status: {request.status.value}"
            )
        
        # Update request
        request.status = ApprovalStatus.APPROVED if response.approved else ApprovalStatus.REJECTED
        request.response_data = {
            "approved": response.approved,
            "feedback": response.feedback,
            "modified_data": response.modified_data,
            "responded_at": datetime.utcnow().isoformat()
        }
        request.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(request)
        
        # Notify via WebSocket
        try:
            from app.services.websocket_service import manager
            await manager.broadcast({
                "type": "approval_response",
                "data": {
                    "request_id": request_id,
                    "approved": response.approved,
                    "workflow_id": request.workflow_id
                }
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast approval response: {e}")
        
        logger.info(f"Processed approval request {request_id}: {'approved' if response.approved else 'rejected'}")
        
        return ApprovalStatusResponse(
            status="processed",
            message=f"Approval request {'approved' if response.approved else 'rejected'}",
            request_id=request_id,
            approved=response.approved
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to respond to approval: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{request_id}", response_model=ApprovalStatusResponse)
async def cancel_approval_request(
    request_id: int,
    db: Session = Depends(get_db)
) -> ApprovalStatusResponse:
    """Cancel a pending approval request.
    
    Marks a pending request as rejected/cancelled. Cannot cancel already
    processed requests.
    
    Args:
        request_id: Approval request identifier
        db: Database session
        
    Returns:
        Status of the cancellation
        
    Raises:
        HTTPException: If request not found or already processed
        
    Example:
        DELETE /api/v1/approvals/123
    """
    try:
        query = select(HumanApprovalRequest).where(
            HumanApprovalRequest.id == request_id
        )
        result = db.exec(query)
        request = result.first()
        
        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Approval request {request_id} not found"
            )
        
        if request.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel request with status: {request.status.value}"
            )
        
        request.status = ApprovalStatus.REJECTED
        request.response_data = {
            "approved": False,
            "feedback": "Request cancelled",
            "cancelled_at": datetime.utcnow().isoformat()
        }
        request.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Cancelled approval request {request_id}")
        
        return ApprovalStatusResponse(
            status="cancelled",
            message="Approval request cancelled",
            request_id=request_id,
            approved=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel approval request: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
