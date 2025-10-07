"""
Integration tests for orchestration API endpoints.
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import HandoffState, PlanReviewRequest


@pytest.mark.integration
class TestHandoffAPI:
    """Test handoff state API endpoints."""
    
    def test_list_handoff_states_empty(self, client: TestClient):
        """Test listing handoff states when none exist."""
        response = client.get("/api/v1/api/orchestration/handoffs")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_and_list_handoff_states(self, client: TestClient, session: Session):
        """Test creating and listing handoff states."""
        # Create handoff states directly in database
        state1 = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-1",
        )
        state2 = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-2",
            previous_agent_id="agent-1",
            handoff_reason="Escalation"
        )
        
        session.add(state1)
        session.add(state2)
        session.commit()
        
        # List all states
        response = client.get("/api/v1/api/orchestration/handoffs")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["workflow_id"] == "workflow-123"
    
    def test_list_handoff_states_filtered_by_workflow(self, client: TestClient, session: Session):
        """Test filtering handoff states by workflow_id."""
        # Create states for different workflows
        state1 = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-1",
        )
        state2 = HandoffState(
            workflow_id="workflow-456",
            current_agent_id="agent-2",
        )
        
        session.add(state1)
        session.add(state2)
        session.commit()
        
        # Filter by workflow_id
        response = client.get("/api/v1/api/orchestration/handoffs?workflow_id=workflow-123")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["workflow_id"] == "workflow-123"
    
    def test_get_handoff_state(self, client: TestClient, session: Session):
        """Test getting a specific handoff state."""
        state = HandoffState(
            workflow_id="workflow-789",
            current_agent_id="agent-3",
            handoff_reason="Specialization"
        )
        
        session.add(state)
        session.commit()
        session.refresh(state)
        
        # Get the state
        response = client.get(f"/api/v1/api/orchestration/handoffs/{state.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == state.id
        assert data["workflow_id"] == "workflow-789"
        assert data["current_agent_id"] == "agent-3"
        assert data["handoff_reason"] == "Specialization"
    
    def test_get_handoff_state_not_found(self, client: TestClient):
        """Test getting non-existent handoff state."""
        response = client.get("/api/v1/api/orchestration/handoffs/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_handoff_states_pagination(self, client: TestClient, session: Session):
        """Test pagination for handoff states."""
        # Create multiple states
        for i in range(5):
            state = HandoffState(
                workflow_id="workflow-pagination",
                current_agent_id=f"agent-{i}",
            )
            session.add(state)
        session.commit()
        
        # Test limit
        response = client.get("/api/v1/api/orchestration/handoffs?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Test offset
        response = client.get("/api/v1/api/orchestration/handoffs?limit=2&offset=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


@pytest.mark.integration
class TestPlanReviewAPI:
    """Test plan review API endpoints."""
    
    def test_list_plan_reviews_empty(self, client: TestClient):
        """Test listing plan reviews when none exist."""
        response = client.get("/api/v1/api/orchestration/plan-reviews")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_and_list_plan_reviews(self, client: TestClient, session: Session):
        """Test creating and listing plan reviews."""
        # Create plan review requests directly in database
        review1 = PlanReviewRequest(
            workflow_id="workflow-123",
            task_text="Build API",
            plan_text="Step 1: Design\nStep 2: Implement",
            status="pending"
        )
        review2 = PlanReviewRequest(
            workflow_id="workflow-123",
            task_text="Add tests",
            plan_text="Step 1: Unit tests\nStep 2: Integration tests",
            status="approved"
        )
        
        session.add(review1)
        session.add(review2)
        session.commit()
        
        # List all reviews
        response = client.get("/api/v1/api/orchestration/plan-reviews")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    def test_list_plan_reviews_filtered_by_status(self, client: TestClient, session: Session):
        """Test filtering plan reviews by status."""
        # Create reviews with different statuses
        review1 = PlanReviewRequest(
            workflow_id="workflow-filter",
            task_text="Task 1",
            plan_text="Plan 1",
            status="pending"
        )
        review2 = PlanReviewRequest(
            workflow_id="workflow-filter",
            task_text="Task 2",
            plan_text="Plan 2",
            status="approved"
        )
        
        session.add(review1)
        session.add(review2)
        session.commit()
        
        # Filter by status
        response = client.get("/api/v1/api/orchestration/plan-reviews?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
    
    def test_get_plan_review(self, client: TestClient, session: Session):
        """Test getting a specific plan review."""
        review = PlanReviewRequest(
            workflow_id="workflow-get",
            task_text="Build feature",
            facts_text="Requirements gathered",
            plan_text="Implementation plan",
            round_index=1,
            status="pending"
        )
        
        session.add(review)
        session.commit()
        session.refresh(review)
        
        # Get the review
        response = client.get(f"/api/v1/api/orchestration/plan-reviews/{review.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == review.id
        assert data["workflow_id"] == "workflow-get"
        assert data["task_text"] == "Build feature"
        assert data["status"] == "pending"
    
    def test_get_plan_review_not_found(self, client: TestClient):
        """Test getting non-existent plan review."""
        response = client.get("/api/v1/api/orchestration/plan-reviews/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_decide_plan_review_approve(self, client: TestClient, session: Session):
        """Test approving a plan review."""
        review = PlanReviewRequest(
            workflow_id="workflow-decide",
            task_text="Implement feature",
            plan_text="Original plan",
            status="pending"
        )
        
        session.add(review)
        session.commit()
        session.refresh(review)
        
        # Approve the review
        response = client.post(
            f"/api/v1/api/orchestration/plan-reviews/{review.id}/decide",
            json={
                "decision": "approve",
                "comments": "Looks good!"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "approved"
        assert data["decision"] == "approve"
        assert data["comments"] == "Looks good!"
        assert data["reviewed_at"] is not None
    
    def test_decide_plan_review_revise(self, client: TestClient, session: Session):
        """Test requesting plan revision."""
        review = PlanReviewRequest(
            workflow_id="workflow-revise",
            task_text="Build API",
            plan_text="Basic plan",
            status="pending"
        )
        
        session.add(review)
        session.commit()
        session.refresh(review)
        
        # Request revision
        response = client.post(
            f"/api/v1/api/orchestration/plan-reviews/{review.id}/decide",
            json={
                "decision": "revise",
                "comments": "Add authentication step",
                "edited_plan_text": "1. Design API\n2. Add authentication\n3. Implement"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "revised"
        assert data["decision"] == "revise"
        assert data["comments"] == "Add authentication step"
        assert data["edited_plan_text"] is not None
        assert data["reviewed_at"] is not None
    
    def test_decide_plan_review_invalid_decision(self, client: TestClient, session: Session):
        """Test invalid decision value."""
        review = PlanReviewRequest(
            workflow_id="workflow-invalid",
            task_text="Task",
            plan_text="Plan",
            status="pending"
        )
        
        session.add(review)
        session.commit()
        session.refresh(review)
        
        # Invalid decision
        response = client.post(
            f"/api/v1/api/orchestration/plan-reviews/{review.id}/decide",
            json={
                "decision": "maybe",  # Invalid
            }
        )
        assert response.status_code == 400
        assert "must be 'approve' or 'revise'" in response.json()["detail"]
    
    def test_decide_plan_review_already_decided(self, client: TestClient, session: Session):
        """Test deciding a plan that's already been reviewed."""
        review = PlanReviewRequest(
            workflow_id="workflow-decided",
            task_text="Task",
            plan_text="Plan",
            status="approved",  # Already decided
            decision="approve"
        )
        
        session.add(review)
        session.commit()
        session.refresh(review)
        
        # Try to decide again
        response = client.post(
            f"/api/v1/api/orchestration/plan-reviews/{review.id}/decide",
            json={
                "decision": "revise",
            }
        )
        assert response.status_code == 400
        assert "already been reviewed" in response.json()["detail"]
    
    def test_decide_plan_review_not_found(self, client: TestClient):
        """Test deciding non-existent plan review."""
        response = client.post(
            "/api/v1/api/orchestration/plan-reviews/99999/decide",
            json={
                "decision": "approve",
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
