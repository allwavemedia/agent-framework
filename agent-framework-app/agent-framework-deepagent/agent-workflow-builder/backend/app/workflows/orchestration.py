"""
Orchestration patterns for multi-agent workflows.

This module provides HandoffBuilder and MagenticBuilder wrappers for the
Microsoft Agent Framework's advanced orchestration patterns.
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from app.core.logging import get_logger
from app.agents.agent_factory import AgentFactory

logger = get_logger(__name__)

# Import Microsoft Agent Framework orchestration components
try:
    from agent_framework import (
        WorkflowBuilder,
        MagenticBuilder as AFMagenticBuilder,
        ChatAgent,
        Workflow,
        WorkflowContext,
    )
    from agent_framework._workflows import (
        MagenticPlanReviewRequest,
        MagenticPlanReviewReply,
        MagenticPlanReviewDecision,
    )
    ORCHESTRATION_AVAILABLE = True
    logger.info("Microsoft Agent Framework orchestration patterns available")
except ImportError as e:
    logger.warning(f"Agent Framework orchestration not available: {e}")
    ORCHESTRATION_AVAILABLE = False
    
    # Mock classes for development without agent_framework installed
    class WorkflowBuilder:
        def __init__(self, start_executor=None):
            self.start_executor = start_executor
            
        def build(self):
            return MockWorkflow()
    
    class AFMagenticBuilder:
        def participants(self, **kwargs):
            return self
        
        def with_plan_review(self, enable=True):
            return self
        
        def build(self):
            return MockWorkflow()
    
    class MockWorkflow:
        async def run(self, input_data):
            return {"result": "Mock orchestration workflow"}
    
    class ChatAgent:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions


class HandoffType(str, Enum):
    """Types of handoffs between agents."""
    ESCALATION = "escalation"  # Escalate to higher authority
    SPECIALIZATION = "specialization"  # Route to specialist
    COLLABORATION = "collaboration"  # Work together
    DELEGATION = "delegation"  # Delegate task
    RETURN = "return"  # Return to previous agent


@dataclass
class HandoffConfig:
    """Configuration for agent-to-agent handoff."""
    from_agent_id: str
    to_agent_id: str
    handoff_type: HandoffType
    reason: Optional[str] = None
    condition: Optional[str] = None


@dataclass
class HandoffState:
    """Current state of a handoff workflow."""
    current_agent_id: str
    history: List[Dict[str, Any]]
    context: Dict[str, Any]


class HandoffBuilder:
    """Builder for creating handoff workflows with agent-to-agent control transfer.
    
    This builder creates workflows where agents can dynamically hand off control
    to other agents based on context or rules. This is particularly useful for:
    - Customer support (triage -> specialist)
    - Expert systems (generalist -> domain expert)
    - Multi-stage processing (stage1 -> stage2 -> stage3)
    
    Example:
        ```python
        async with AgentFactory() as factory:
            triage = await factory.create_agent(triage_config)
            tech = await factory.create_agent(tech_config)
            sales = await factory.create_agent(sales_config)
            
            builder = HandoffBuilder()
            workflow = await builder.start_handoff_with(triage)\\
                .with_handoff(triage, tech, "Technical questions")\\
                .with_handoff(triage, sales, "Sales inquiries")\\
                .build()
            
            result = await workflow.run("I need API integration help")
        ```
    """
    
    def __init__(self):
        """Initialize HandoffBuilder."""
        self.logger = get_logger(__name__)
        self._initial_agent = None
        self._handoffs: List[HandoffConfig] = []
        self._agents: Dict[str, Any] = {}
    
    def start_handoff_with(self, agent: Any) -> "HandoffBuilder":
        """Set the initial agent for the handoff workflow.
        
        Args:
            agent: Initial agent (ChatAgent or compatible)
            
        Returns:
            Self for method chaining
        """
        self._initial_agent = agent
        # Store agent by ID or name
        agent_id = getattr(agent, 'id', None) or getattr(agent, 'name', 'agent')
        self._agents[agent_id] = agent
        self.logger.info(f"Starting handoff workflow with agent: {agent_id}")
        return self
    
    def with_handoff(
        self,
        from_agent: Any,
        to_agent: Any,
        reason: Optional[str] = None,
        handoff_type: HandoffType = HandoffType.SPECIALIZATION
    ) -> "HandoffBuilder":
        """Add a handoff relationship between two agents.
        
        Args:
            from_agent: Source agent
            to_agent: Target agent
            reason: Optional reason for the handoff
            handoff_type: Type of handoff relationship
            
        Returns:
            Self for method chaining
        """
        from_id = getattr(from_agent, 'id', None) or getattr(from_agent, 'name', 'from_agent')
        to_id = getattr(to_agent, 'id', None) or getattr(to_agent, 'name', 'to_agent')
        
        # Store agents
        self._agents[from_id] = from_agent
        self._agents[to_id] = to_agent
        
        # Create handoff config
        config = HandoffConfig(
            from_agent_id=from_id,
            to_agent_id=to_id,
            handoff_type=handoff_type,
            reason=reason
        )
        self._handoffs.append(config)
        
        self.logger.info(f"Added handoff: {from_id} -> {to_id} ({handoff_type.value})")
        return self
    
    async def build(self) -> Any:
        """Build the handoff workflow.
        
        Returns:
            Workflow object ready for execution
            
        Raises:
            ValueError: If initial agent not set or no handoffs configured
        """
        if not self._initial_agent:
            raise ValueError("Initial agent must be set with start_handoff_with()")
        
        if not self._handoffs:
            self.logger.warning("No handoffs configured - workflow will run with single agent")
        
        if not ORCHESTRATION_AVAILABLE:
            self.logger.warning("Using mock workflow - agent_framework not available")
            return MockWorkflow()
        
        # Build workflow using Microsoft Agent Framework patterns
        # In a real implementation, this would use the framework's WorkflowBuilder
        # to create proper agent executors with handoff functions
        builder = WorkflowBuilder()
        
        # TODO: Implement proper handoff workflow construction using
        # the pattern from dotnet/src/Microsoft.Agents.AI.Workflows/AgentWorkflowBuilder.cs
        # This would involve:
        # 1. Creating AgentExecutors for each agent
        # 2. Adding handoff functions to agents
        # 3. Connecting executors with edges based on handoff configs
        
        self.logger.info(f"Built handoff workflow with {len(self._agents)} agents and {len(self._handoffs)} handoffs")
        return builder.build()


class MagenticBuilder:
    """Builder for creating Magentic One multi-agent collaboration workflows.
    
    This is a wrapper around the Agent Framework's MagenticBuilder that provides
    application-specific configuration and integration with the workflow builder
    backend.
    
    Magentic One enables multiple specialist agents to collaborate on complex tasks
    with a manager agent coordinating their efforts. It supports:
    - Plan review (human-in-the-loop for plan approval)
    - Progress tracking
    - Dynamic agent selection
    - Error recovery
    
    Example:
        ```python
        async with AgentFactory() as factory:
            researcher = await factory.create_agent(researcher_config)
            coder = await factory.create_agent(coder_config)
            reviewer = await factory.create_agent(reviewer_config)
            
            builder = MagenticBuilder()
            workflow = await builder.participants(
                researcher=researcher,
                coder=coder,
                reviewer=reviewer
            ).with_plan_review().build()
            
            result = await workflow.run("Build a REST API for user management")
        ```
    """
    
    def __init__(self, chat_client=None):
        """Initialize MagenticBuilder.
        
        Args:
            chat_client: Optional chat client for the manager agent
        """
        self.logger = get_logger(__name__)
        self._chat_client = chat_client
        self._participants: Dict[str, Any] = {}
        self._enable_plan_review = False
        self._checkpoint_storage = None
        
        if ORCHESTRATION_AVAILABLE:
            self._builder = AFMagenticBuilder()
        else:
            self.logger.warning("Agent Framework not available - using mock builder")
            self._builder = AFMagenticBuilder()
    
    def participants(self, **agents) -> "MagenticBuilder":
        """Add participant agents to the workflow.
        
        Args:
            **agents: Keyword arguments mapping role names to agents
                     e.g., researcher=agent1, coder=agent2
        
        Returns:
            Self for method chaining
        """
        self._participants.update(agents)
        
        if ORCHESTRATION_AVAILABLE:
            self._builder.participants(**agents)
        
        self.logger.info(f"Added {len(agents)} participants: {list(agents.keys())}")
        return self
    
    def with_plan_review(self, enable: bool = True) -> "MagenticBuilder":
        """Enable plan review (human-in-the-loop) before execution.
        
        When enabled, the workflow will pause after plan generation and wait
        for human approval before proceeding with execution.
        
        Args:
            enable: Whether to enable plan review (default: True)
            
        Returns:
            Self for method chaining
        """
        self._enable_plan_review = enable
        
        if ORCHESTRATION_AVAILABLE:
            self._builder.with_plan_review(enable)
        
        self.logger.info(f"Plan review {'enabled' if enable else 'disabled'}")
        return self
    
    def with_checkpointing(self, checkpoint_storage) -> "MagenticBuilder":
        """Enable workflow state checkpointing.
        
        Args:
            checkpoint_storage: CheckpointStorage instance for persistence
            
        Returns:
            Self for method chaining
        """
        self._checkpoint_storage = checkpoint_storage
        
        if ORCHESTRATION_AVAILABLE:
            self._builder.with_checkpointing(checkpoint_storage)
        
        self.logger.info("Checkpointing enabled")
        return self
    
    def with_standard_manager(self, chat_client=None, **kwargs) -> "MagenticBuilder":
        """Configure the Magentic manager agent.
        
        Args:
            chat_client: Chat client for the manager
            **kwargs: Additional manager configuration options
            
        Returns:
            Self for method chaining
        """
        client = chat_client or self._chat_client
        
        if ORCHESTRATION_AVAILABLE and client:
            self._builder.with_standard_manager(chat_client=client, **kwargs)
            self.logger.info("Standard manager configured")
        
        return self
    
    async def build(self) -> Any:
        """Build the Magentic One workflow.
        
        Returns:
            Workflow object ready for execution
            
        Raises:
            ValueError: If no participants configured
        """
        if not self._participants:
            raise ValueError("At least one participant must be added")
        
        if not ORCHESTRATION_AVAILABLE:
            self.logger.warning("Using mock workflow - agent_framework not available")
            return MockWorkflow()
        
        # Build the workflow
        workflow = self._builder.build()
        
        self.logger.info(
            f"Built Magentic workflow with {len(self._participants)} participants, "
            f"plan_review={self._enable_plan_review}"
        )
        
        return workflow


# Plan review data structures (for API serialization)
@dataclass
class PlanReviewRequest:
    """Plan review request for human approval."""
    request_id: str
    workflow_id: str
    task_text: str
    facts_text: str
    plan_text: str
    round_index: int
    created_at: str


@dataclass
class PlanReviewResponse:
    """Human response to a plan review request."""
    request_id: str
    decision: str  # "approve" or "revise"
    edited_plan_text: Optional[str] = None
    comments: Optional[str] = None
