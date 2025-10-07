"""
Database models for the Agent Workflow Builder.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import BaseModel, ConfigDict


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent types supported by the system."""
    CHAT_AGENT = "chat_agent"
    SPECIALIST_AGENT = "specialist_agent"
    TOOL_AGENT = "tool_agent"
    CUSTOM_AGENT = "custom_agent"


class ExecutorType(str, Enum):
    """Executor types for workflow nodes."""
    AGENT = "agent"
    FUNCTION = "function"
    CONDITION = "condition"
    HUMAN_INPUT = "human_input"
    CUSTOM = "custom"


class ApprovalStatus(str, Enum):
    """Approval request status for HITL workflows."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


# Base models
class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# Agent models
class AgentBase(SQLModel):
    """Base agent model."""
    name: str = Field(index=True, description="Agent name")
    description: Optional[str] = Field(default=None, description="Agent description")
    agent_type: AgentType = Field(description="Type of agent")
    instructions: str = Field(description="Agent instructions/system prompt")
    model_settings: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Model configuration settings")
    tools: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = Field(default=True, description="Whether the agent is active")


class Agent(AgentBase, TimestampMixin, table=True):
    """Agent database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    workflow_nodes: List["WorkflowNode"] = Relationship(back_populates="agent")


class AgentCreate(AgentBase):
    """Agent creation model."""
    pass


class AgentUpdate(SQLModel):
    """Agent update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    model_settings: Optional[Dict[str, Any]] = None
    tools: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """Agent response model."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Workflow models
class WorkflowBase(SQLModel):
    """Base workflow model."""
    name: str = Field(index=True, description="Workflow name")
    description: Optional[str] = Field(default=None, description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_template: bool = Field(default=False, description="Whether this is a template")
    is_public: bool = Field(default=False, description="Whether this workflow is public")


class Workflow(WorkflowBase, TimestampMixin, table=True):
    """Workflow database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    nodes: List["WorkflowNode"] = Relationship(back_populates="workflow")
    edges: List["WorkflowEdge"] = Relationship(back_populates="workflow")
    executions: List["WorkflowExecution"] = Relationship(back_populates="workflow")


class WorkflowCreate(WorkflowBase):
    """Workflow creation model."""
    pass


class WorkflowUpdate(SQLModel):
    """Workflow update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_public: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Workflow response model."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    nodes: List["WorkflowNodeResponse"] = []
    edges: List["WorkflowEdgeResponse"] = []


# Workflow node models
class WorkflowNodeBase(SQLModel):
    """Base workflow node model."""
    name: str = Field(description="Node name")
    executor_type: ExecutorType = Field(description="Type of executor")
    position_x: float = Field(description="X position in the visual editor")
    position_y: float = Field(description="Y position in the visual editor")
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    is_start_node: bool = Field(default=False, description="Whether this is the start node")
    is_output_node: bool = Field(default=False, description="Whether this is an output node")


class WorkflowNode(WorkflowNodeBase, TimestampMixin, table=True):
    """Workflow node database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    agent_id: Optional[int] = Field(default=None, foreign_key="agent.id")
    
    # Relationships
    workflow: Workflow = Relationship(back_populates="nodes")
    agent: Optional[Agent] = Relationship(back_populates="workflow_nodes")
    source_edges: List["WorkflowEdge"] = Relationship(
        back_populates="source_node",
        sa_relationship_kwargs={"foreign_keys": "WorkflowEdge.source_node_id"}
    )
    target_edges: List["WorkflowEdge"] = Relationship(
        back_populates="target_node",
        sa_relationship_kwargs={"foreign_keys": "WorkflowEdge.target_node_id"}
    )


class WorkflowNodeCreate(WorkflowNodeBase):
    """Workflow node creation model."""
    workflow_id: int
    agent_id: Optional[int] = None


class WorkflowNodeUpdate(SQLModel):
    """Workflow node update model."""
    name: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    config: Optional[Dict[str, Any]] = None
    is_start_node: Optional[bool] = None
    agent_id: Optional[int] = None


class WorkflowNodeResponse(WorkflowNodeBase):
    """Workflow node response model."""
    id: int
    workflow_id: int
    agent_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


# Workflow edge models
class WorkflowEdgeBase(SQLModel):
    """Base workflow edge model."""
    label: Optional[str] = Field(default=None, description="Edge label")
    condition: Optional[str] = Field(default=None, description="Edge condition (Python expression)")
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class WorkflowEdge(WorkflowEdgeBase, TimestampMixin, table=True):
    """Workflow edge database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    source_node_id: int = Field(foreign_key="workflownode.id")
    target_node_id: int = Field(foreign_key="workflownode.id")
    
    # Relationships
    workflow: Workflow = Relationship(back_populates="edges")
    source_node: WorkflowNode = Relationship(
        back_populates="source_edges",
        sa_relationship_kwargs={"foreign_keys": "WorkflowEdge.source_node_id"}
    )
    target_node: WorkflowNode = Relationship(
        back_populates="target_edges",
        sa_relationship_kwargs={"foreign_keys": "WorkflowEdge.target_node_id"}
    )


class WorkflowEdgeCreate(WorkflowEdgeBase):
    """Workflow edge creation model."""
    workflow_id: int
    source_node_id: int
    target_node_id: int


class WorkflowEdgeUpdate(SQLModel):
    """Workflow edge update model."""
    label: Optional[str] = None
    condition: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class WorkflowEdgeResponse(WorkflowEdgeBase):
    """Workflow edge response model."""
    id: int
    workflow_id: int
    source_node_id: int
    target_node_id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Workflow execution models
class WorkflowExecutionBase(SQLModel):
    """Base workflow execution model."""
    status: WorkflowStatus = Field(default=WorkflowStatus.RUNNING)
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    error_message: Optional[str] = Field(default=None)
    execution_log: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class WorkflowExecution(WorkflowExecutionBase, TimestampMixin, table=True):
    """Workflow execution database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    
    # Relationships
    workflow: Workflow = Relationship(back_populates="executions")


class WorkflowExecutionCreate(SQLModel):
    """Workflow execution creation model."""
    workflow_id: int
    input_data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionUpdate(SQLModel):
    """Workflow execution update model."""
    status: Optional[WorkflowStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_log: Optional[List[Dict[str, Any]]] = None
    completed_at: Optional[datetime] = None


class WorkflowExecutionResponse(WorkflowExecutionBase):
    """Workflow execution response model."""
    id: int
    workflow_id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Workflow checkpoint models
class WorkflowCheckpoint(SQLModel, table=True):
    """Workflow checkpoint storage for state persistence."""
    __tablename__ = "workflow_checkpoints"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str = Field(index=True, description="Workflow identifier")
    checkpoint_id: str = Field(index=True, description="Checkpoint identifier")
    state_data: Dict[str, Any] = Field(sa_column=Column(JSON), description="Serialized workflow state")
    checkpoint_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Human-in-the-Loop models
class HumanApprovalRequest(SQLModel, table=True):
    """Human approval requests for HITL workflows."""
    __tablename__ = "human_approval_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str = Field(index=True, description="Workflow identifier")
    request_type: str = Field(description="Type of approval request")
    request_data: Dict[str, Any] = Field(sa_column=Column(JSON), description="Request data")
    response_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Response data")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Approval status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# Orchestration models for Handoff and Magentic patterns
class HandoffState(SQLModel, table=True):
    """Handoff state tracking for agent-to-agent control transfer."""
    __tablename__ = "handoff_states"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str = Field(index=True, description="Associated workflow ID")
    execution_id: Optional[int] = Field(default=None, description="Optional execution ID reference")
    current_agent_id: str = Field(description="Currently active agent")
    previous_agent_id: Optional[str] = Field(default=None, description="Previous agent in handoff chain")
    handoff_reason: Optional[str] = Field(default=None, description="Reason for handoff")
    context_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Handoff context data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class PlanReviewRequest(SQLModel, table=True):
    """Plan review requests for Magentic One workflows."""
    __tablename__ = "plan_review_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str = Field(index=True, description="Associated workflow ID")
    execution_id: Optional[int] = Field(default=None, description="Optional execution ID reference")
    task_text: str = Field(description="Original task description")
    facts_text: str = Field(default="", description="Gathered facts")
    plan_text: str = Field(description="Generated plan requiring review")
    round_index: int = Field(default=0, description="Review round number")
    status: str = Field(default="pending", description="Review status: pending, approved, revised")
    decision: Optional[str] = Field(default=None, description="approve or revise")
    edited_plan_text: Optional[str] = Field(default=None, description="Human-edited plan")
    comments: Optional[str] = Field(default=None, description="Human feedback")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(default=None)


# WebSocket message models
class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowExecutionEvent(BaseModel):
    """Workflow execution event model."""
    execution_id: int
    event_type: str
    node_id: Optional[int] = None
    data: Dict[str, Any]


# Context Provider & Memory Models
class ConversationMemory(SQLModel, table=True):
    """Conversation memory storage for context providers."""
    __tablename__ = "conversation_memories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True, description="Thread identifier")
    agent_id: Optional[int] = Field(default=None, index=True, description="Associated agent")
    user_id: Optional[str] = Field(default=None, index=True, description="User identifier")
    memory_key: str = Field(index=True, description="Memory key/category")
    memory_value: Dict[str, Any] = Field(sa_column=Column(JSON), description="Memory content")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ContextProviderConfig(SQLModel, table=True):
    """Configuration for context providers."""
    __tablename__ = "context_provider_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="Provider name")
    provider_type: str = Field(description="Type of context provider (simple, mem0, redis, custom)")
    config: Dict[str, Any] = Field(sa_column=Column(JSON), description="Provider configuration")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ContextProviderConfigCreate(BaseModel):
    """Model for creating context provider config."""
    name: str
    provider_type: str
    config: Dict[str, Any]


class ContextProviderConfigResponse(BaseModel):
    """Response model for context provider config."""
    id: int
    name: str
    provider_type: str
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    timestamp: datetime = Field(default_factory=datetime.utcnow)