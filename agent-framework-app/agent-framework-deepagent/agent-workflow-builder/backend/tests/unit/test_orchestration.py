"""
Unit tests for orchestration patterns (HandoffBuilder and MagenticBuilder).
"""
import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.workflows.orchestration import (
    HandoffBuilder,
    MagenticBuilder,
    HandoffType,
    HandoffConfig,
    PlanReviewRequest as PlanReviewDTO,
    PlanReviewResponse,
)
from app.models import HandoffState, PlanReviewRequest


@pytest.mark.unit
class TestHandoffBuilder:
    """Test HandoffBuilder functionality."""
    
    def test_handoff_builder_initialization(self):
        """Test HandoffBuilder can be initialized."""
        builder = HandoffBuilder()
        assert builder is not None
        assert builder._initial_agent is None
        assert builder._handoffs == []
        assert builder._agents == {}
    
    def test_start_handoff_with(self):
        """Test setting initial agent."""
        # Mock agent
        class MockAgent:
            def __init__(self, agent_id):
                self.id = agent_id
                self.name = f"agent-{agent_id}"
        
        builder = HandoffBuilder()
        agent = MockAgent("agent-1")
        
        result = builder.start_handoff_with(agent)
        assert result == builder  # Should return self for chaining
        assert builder._initial_agent == agent
        assert "agent-1" in builder._agents
    
    def test_with_handoff(self):
        """Test adding handoff relationships."""
        class MockAgent:
            def __init__(self, agent_id):
                self.id = agent_id
                self.name = f"agent-{agent_id}"
        
        builder = HandoffBuilder()
        agent1 = MockAgent("triage")
        agent2 = MockAgent("specialist")
        
        builder.start_handoff_with(agent1)
        result = builder.with_handoff(agent1, agent2, "Technical issues")
        
        assert result == builder  # Should return self for chaining
        assert len(builder._handoffs) == 1
        assert builder._handoffs[0].from_agent_id == "triage"
        assert builder._handoffs[0].to_agent_id == "specialist"
        assert builder._handoffs[0].reason == "Technical issues"
    
    @pytest.mark.asyncio
    async def test_build_without_initial_agent(self):
        """Test build raises error without initial agent."""
        builder = HandoffBuilder()
        
        with pytest.raises(ValueError, match="Initial agent must be set"):
            await builder.build()
    
    @pytest.mark.asyncio
    async def test_build_with_initial_agent(self):
        """Test build succeeds with initial agent."""
        class MockAgent:
            def __init__(self, agent_id):
                self.id = agent_id
                self.name = f"agent-{agent_id}"
        
        builder = HandoffBuilder()
        agent = MockAgent("agent-1")
        
        builder.start_handoff_with(agent)
        workflow = await builder.build()
        
        assert workflow is not None
    
    def test_handoff_types(self):
        """Test HandoffType enum values."""
        assert HandoffType.ESCALATION == "escalation"
        assert HandoffType.SPECIALIZATION == "specialization"
        assert HandoffType.COLLABORATION == "collaboration"
        assert HandoffType.DELEGATION == "delegation"
        assert HandoffType.RETURN == "return"


@pytest.mark.unit
class TestMagenticBuilder:
    """Test MagenticBuilder functionality."""
    
    def test_magentic_builder_initialization(self):
        """Test MagenticBuilder can be initialized."""
        builder = MagenticBuilder()
        assert builder is not None
        assert builder._participants == {}
        assert builder._enable_plan_review is False
    
    def test_participants(self):
        """Test adding participants."""
        class MockAgent:
            def __init__(self, agent_id):
                self.id = agent_id
                self.name = f"agent-{agent_id}"
        
        builder = MagenticBuilder()
        researcher = MockAgent("researcher")
        coder = MockAgent("coder")
        
        result = builder.participants(researcher=researcher, coder=coder)
        
        assert result == builder  # Should return self for chaining
        assert len(builder._participants) == 2
        assert "researcher" in builder._participants
        assert "coder" in builder._participants
    
    def test_with_plan_review(self):
        """Test enabling plan review."""
        builder = MagenticBuilder()
        
        result = builder.with_plan_review(True)
        
        assert result == builder  # Should return self for chaining
        assert builder._enable_plan_review is True
        
        # Test disabling
        builder.with_plan_review(False)
        assert builder._enable_plan_review is False
    
    def test_with_checkpointing(self):
        """Test enabling checkpointing."""
        class MockCheckpointStorage:
            pass
        
        builder = MagenticBuilder()
        storage = MockCheckpointStorage()
        
        result = builder.with_checkpointing(storage)
        
        assert result == builder  # Should return self for chaining
        assert builder._checkpoint_storage == storage
    
    @pytest.mark.asyncio
    async def test_build_without_participants(self):
        """Test build raises error without participants."""
        builder = MagenticBuilder()
        
        with pytest.raises(ValueError, match="At least one participant must be added"):
            await builder.build()
    
    @pytest.mark.asyncio
    async def test_build_with_participants(self):
        """Test build succeeds with participants."""
        class MockAgent:
            def __init__(self, agent_id):
                self.id = agent_id
                self.name = f"agent-{agent_id}"
        
        builder = MagenticBuilder()
        agent = MockAgent("agent-1")
        
        builder.participants(agent=agent)
        workflow = await builder.build()
        
        assert workflow is not None


@pytest.mark.unit
class TestHandoffState:
    """Test HandoffState database model."""
    
    def test_handoff_state_creation(self, session: Session):
        """Test creating a handoff state record."""
        state = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-2",
            previous_agent_id="agent-1",
            handoff_reason="Escalation to specialist",
            context_data={"topic": "technical"}
        )
        
        session.add(state)
        session.commit()
        session.refresh(state)
        
        assert state.id is not None
        assert state.workflow_id == "workflow-123"
        assert state.current_agent_id == "agent-2"
        assert state.previous_agent_id == "agent-1"
        assert state.handoff_reason == "Escalation to specialist"
        assert state.context_data["topic"] == "technical"
        assert isinstance(state.created_at, datetime)
    
    def test_handoff_state_query(self, session: Session):
        """Test querying handoff states."""
        # Create multiple states
        state1 = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-1",
        )
        state2 = HandoffState(
            workflow_id="workflow-123",
            current_agent_id="agent-2",
            previous_agent_id="agent-1",
        )
        
        session.add(state1)
        session.add(state2)
        session.commit()
        
        # Query by workflow
        statement = select(HandoffState).where(HandoffState.workflow_id == "workflow-123")
        states = session.exec(statement).all()
        
        assert len(states) == 2


@pytest.mark.unit
class TestPlanReviewRequest:
    """Test PlanReviewRequest database model."""
    
    def test_plan_review_request_creation(self, session: Session):
        """Test creating a plan review request."""
        request = PlanReviewRequest(
            workflow_id="workflow-456",
            task_text="Build a REST API",
            facts_text="User needs CRUD operations",
            plan_text="1. Design endpoints\n2. Implement handlers\n3. Add tests",
            round_index=0,
            status="pending"
        )
        
        session.add(request)
        session.commit()
        session.refresh(request)
        
        assert request.id is not None
        assert request.workflow_id == "workflow-456"
        assert request.task_text == "Build a REST API"
        assert request.status == "pending"
        assert request.round_index == 0
        assert request.decision is None
        assert isinstance(request.created_at, datetime)
    
    def test_plan_review_approval(self, session: Session):
        """Test approving a plan review."""
        request = PlanReviewRequest(
            workflow_id="workflow-456",
            task_text="Build a REST API",
            plan_text="Plan content",
            status="pending"
        )
        
        session.add(request)
        session.commit()
        
        # Approve the plan
        request.status = "approved"
        request.decision = "approve"
        request.reviewed_at = datetime.utcnow()
        
        session.add(request)
        session.commit()
        session.refresh(request)
        
        assert request.status == "approved"
        assert request.decision == "approve"
        assert request.reviewed_at is not None
    
    def test_plan_review_revision(self, session: Session):
        """Test requesting plan revision."""
        request = PlanReviewRequest(
            workflow_id="workflow-456",
            task_text="Build a REST API",
            plan_text="Initial plan",
            status="pending"
        )
        
        session.add(request)
        session.commit()
        
        # Request revision
        request.status = "revised"
        request.decision = "revise"
        request.comments = "Add authentication step"
        request.reviewed_at = datetime.utcnow()
        
        session.add(request)
        session.commit()
        session.refresh(request)
        
        assert request.status == "revised"
        assert request.decision == "revise"
        assert request.comments == "Add authentication step"
        assert request.reviewed_at is not None


@pytest.mark.unit
def test_plan_review_dto():
    """Test PlanReviewRequest DTO."""
    dto = PlanReviewDTO(
        request_id="req-123",
        workflow_id="workflow-789",
        task_text="Task description",
        facts_text="Facts",
        plan_text="Plan steps",
        round_index=0,
        created_at="2024-01-01T00:00:00Z"
    )
    
    assert dto.request_id == "req-123"
    assert dto.workflow_id == "workflow-789"
    assert dto.task_text == "Task description"


@pytest.mark.unit
def test_plan_review_response_dto():
    """Test PlanReviewResponse DTO."""
    response = PlanReviewResponse(
        request_id="req-123",
        decision="approve",
        edited_plan_text=None,
        comments="Looks good"
    )
    
    assert response.request_id == "req-123"
    assert response.decision == "approve"
    assert response.comments == "Looks good"
