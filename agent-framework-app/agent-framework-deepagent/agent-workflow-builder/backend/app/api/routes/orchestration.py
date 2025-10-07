"""
API routes for orchestration patterns (Handoff and Magentic).
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.logging import get_logger
from app.models import HandoffState, PlanReviewRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/api/orchestration", tags=["orchestration"])


# Request/Response models
class HandoffStateResponse(BaseModel):
    """Response model for handoff state."""
    id: int
    workflow_id: str
    execution_id: Optional[int]
    current_agent_id: str
    previous_agent_id: Optional[str]
    handoff_reason: Optional[str]
    context_data: dict
    created_at: datetime
    updated_at: Optional[datetime]


class PlanReviewRequestResponse(BaseModel):
    """Response model for plan review request."""
    id: int
    workflow_id: str
    execution_id: Optional[int]
    task_text: str
    facts_text: str
    plan_text: str
    round_index: int
    status: str
    decision: Optional[str]
    edited_plan_text: Optional[str]
    comments: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]


class PlanReviewDecision(BaseModel):
    """Request model for plan review decision."""
    decision: str  # "approve" or "revise"
    edited_plan_text: Optional[str] = None
    comments: Optional[str] = None


# Handoff State endpoints
@router.get("/handoffs", response_model=List[HandoffStateResponse])
async def list_handoff_states(
    workflow_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List handoff states, optionally filtered by workflow_id.
    
    Args:
        workflow_id: Optional workflow ID to filter by
        limit: Maximum number of results (default: 50)
        offset: Offset for pagination (default: 0)
        db: Database session
    
    Returns:
        List of handoff states
    """
    try:
        statement = select(HandoffState)
        
        if workflow_id:
            statement = statement.where(HandoffState.workflow_id == workflow_id)
        
        statement = statement.order_by(HandoffState.created_at.desc())
        statement = statement.limit(limit).offset(offset)
        
        results = db.exec(statement).all()
        
        return [
            HandoffStateResponse(
                id=r.id,
                workflow_id=r.workflow_id,
                execution_id=r.execution_id,
                current_agent_id=r.current_agent_id,
                previous_agent_id=r.previous_agent_id,
                handoff_reason=r.handoff_reason,
                context_data=r.context_data,
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error listing handoff states: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list handoff states: {str(e)}"
        )


@router.get("/handoffs/{handoff_id}", response_model=HandoffStateResponse)
async def get_handoff_state(
    handoff_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific handoff state by ID.
    
    Args:
        handoff_id: Handoff state ID
        db: Database session
    
    Returns:
        Handoff state details
    """
    try:
        handoff = db.get(HandoffState, handoff_id)
        
        if not handoff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Handoff state {handoff_id} not found"
            )
        
        return HandoffStateResponse(
            id=handoff.id,
            workflow_id=handoff.workflow_id,
            execution_id=handoff.execution_id,
            current_agent_id=handoff.current_agent_id,
            previous_agent_id=handoff.previous_agent_id,
            handoff_reason=handoff.handoff_reason,
            context_data=handoff.context_data,
            created_at=handoff.created_at,
            updated_at=handoff.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting handoff state {handoff_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get handoff state: {str(e)}"
        )


# Plan Review endpoints
@router.get("/plan-reviews", response_model=List[PlanReviewRequestResponse])
async def list_plan_reviews(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List plan review requests, optionally filtered.
    
    Args:
        workflow_id: Optional workflow ID to filter by
        status: Optional status to filter by (pending, approved, revised)
        limit: Maximum number of results (default: 50)
        offset: Offset for pagination (default: 0)
        db: Database session
    
    Returns:
        List of plan review requests
    """
    try:
        statement = select(PlanReviewRequest)
        
        if workflow_id:
            statement = statement.where(PlanReviewRequest.workflow_id == workflow_id)
        
        if status:
            statement = statement.where(PlanReviewRequest.status == status)
        
        statement = statement.order_by(PlanReviewRequest.created_at.desc())
        statement = statement.limit(limit).offset(offset)
        
        results = db.exec(statement).all()
        
        return [
            PlanReviewRequestResponse(
                id=r.id,
                workflow_id=r.workflow_id,
                execution_id=r.execution_id,
                task_text=r.task_text,
                facts_text=r.facts_text,
                plan_text=r.plan_text,
                round_index=r.round_index,
                status=r.status,
                decision=r.decision,
                edited_plan_text=r.edited_plan_text,
                comments=r.comments,
                created_at=r.created_at,
                reviewed_at=r.reviewed_at
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"Error listing plan reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list plan reviews: {str(e)}"
        )


@router.get("/plan-reviews/{review_id}", response_model=PlanReviewRequestResponse)
async def get_plan_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific plan review request by ID.
    
    Args:
        review_id: Plan review request ID
        db: Database session
    
    Returns:
        Plan review request details
    """
    try:
        review = db.get(PlanReviewRequest, review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan review {review_id} not found"
            )
        
        return PlanReviewRequestResponse(
            id=review.id,
            workflow_id=review.workflow_id,
            execution_id=review.execution_id,
            task_text=review.task_text,
            facts_text=review.facts_text,
            plan_text=review.plan_text,
            round_index=review.round_index,
            status=review.status,
            decision=review.decision,
            edited_plan_text=review.edited_plan_text,
            comments=review.comments,
            created_at=review.created_at,
            reviewed_at=review.reviewed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan review {review_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plan review: {str(e)}"
        )


@router.post("/plan-reviews/{review_id}/decide", response_model=PlanReviewRequestResponse)
async def decide_plan_review(
    review_id: int,
    decision: PlanReviewDecision,
    db: Session = Depends(get_db)
):
    """Submit a decision for a plan review request.
    
    Args:
        review_id: Plan review request ID
        decision: Decision details (approve/revise with optional comments)
        db: Database session
    
    Returns:
        Updated plan review request
    """
    try:
        review = db.get(PlanReviewRequest, review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan review {review_id} not found"
            )
        
        if review.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plan review {review_id} has already been reviewed (status: {review.status})"
            )
        
        # Validate decision
        if decision.decision not in ["approve", "revise"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Decision must be 'approve' or 'revise'"
            )
        
        # Update review
        review.decision = decision.decision
        review.status = "approved" if decision.decision == "approve" else "revised"
        review.reviewed_at = datetime.utcnow()
        
        if decision.edited_plan_text:
            review.edited_plan_text = decision.edited_plan_text
        
        if decision.comments:
            review.comments = decision.comments
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        logger.info(f"Plan review {review_id} decided: {decision.decision}")
        
        return PlanReviewRequestResponse(
            id=review.id,
            workflow_id=review.workflow_id,
            execution_id=review.execution_id,
            task_text=review.task_text,
            facts_text=review.facts_text,
            plan_text=review.plan_text,
            round_index=review.round_index,
            status=review.status,
            decision=review.decision,
            edited_plan_text=review.edited_plan_text,
            comments=review.comments,
            created_at=review.created_at,
            reviewed_at=review.reviewed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deciding plan review {review_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decide plan review: {str(e)}"
        )
