# Implementation Guide - Multi-Provider Edition

**Version:** 2.0 (Multi-Provider)  
**Date:** October 7, 2025  
**Status:** ✅ READY FOR IMPLEMENTATION  
**Verified With:** Microsoft Learn MCP Tools  
**Reference:** See [../agent-framework.md](../agent-framework.md) for complete Agent Framework documentation

---

## 📋 Quick Navigation

- [Overview](#overview)
- [Provider Support](#provider-support)
- [Implementation Tasks](#implementation-tasks)
  - [HIGH PRIORITY](#high-priority-tasks)
  - [MEDIUM PRIORITY](#medium-priority-tasks)
  - [LOW PRIORITY](#low-priority-tasks)
- [Testing Requirements](#testing-requirements)
- [Success Metrics](#success-metrics)

---

## Overview

This guide provides detailed implementation specifications for 18 enhancement tasks. All code examples are **provider-agnostic** and work with:

- **Azure OpenAI** - Enterprise/Production
- **OpenAI Direct** - Rapid Development  
- **Local Models** - Development/Privacy

### Backend Already Supports Multi-Provider

The `AgentFactory` in `backend/app/agents/agent_factory.py` already implements multi-provider support:

```python
class ModelProvider(str, Enum):
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    LOCAL = "local"

# Auto-detection priority: Local > OpenAI > Azure OpenAI
```

**Your task:** Implement missing Agent Framework features using provider-agnostic patterns.

---

## Provider Support

### Creating Agents - All Three Providers

All code in this guide follows these patterns:

**Azure OpenAI:**
```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

chat_client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    credential=AzureCliCredential()
)
agent = chat_client.create_agent(
    instructions="...",
    name="MyAgent"
)
```

**OpenAI Direct:**
```python
from agent_framework.openai import OpenAIChatClient

chat_client = OpenAIChatClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_id=os.getenv("OPENAI_MODEL")
)
agent = chat_client.create_agent(
    instructions="...",
    name="MyAgent"
)
```

**Local Model (Ollama/LM Studio):**
```python
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

local_client = AsyncOpenAI(
    api_key="not-needed",
    base_url=os.getenv("LOCAL_MODEL_BASE_URL")
)
chat_client = OpenAIChatClient(
    client=local_client,
    model=os.getenv("LOCAL_MODEL_NAME")
)
agent = chat_client.create_agent(
    instructions="...",
    name="MyAgent"
)
```

### Using AgentFactory (Provider-Agnostic)

The recommended pattern uses AgentFactory which handles provider selection automatically:

```python
from app.agents.agent_factory import AgentFactory
from app.models import Agent, AgentType

# AgentFactory auto-detects provider from environment
async with AgentFactory() as factory:
    agent = await factory.create_agent(agent_config)
    response = await factory.run_agent(agent, "Hello!")
```

---

## Implementation Tasks

### HIGH PRIORITY TASKS

These are **production-critical** features from the Microsoft Agent Framework.

---

#### Task 1: Checkpointing & State Persistence

**Priority:** 🔴 CRITICAL  
**Effort:** 16-20 hours  
**Provider Support:** All providers

**Overview:**
Implement workflow checkpointing using Agent Framework patterns to enable save/resume of long-running workflows.

**Reference:** See ../agent-framework.md, search for "FileCheckpointStorage" and "CheckpointManager"

##### Backend Implementation

**1. Create Checkpoint Storage** (`backend/app/workflows/checkpoint_storage.py`):

```python
"""Checkpoint storage for workflow state persistence."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlmodel import Session, select
from app.models import WorkflowCheckpoint
from app.core.logging import get_logger

logger = get_logger(__name__)

class DatabaseCheckpointStorage:
    """PostgreSQL-backed checkpoint storage compatible with Agent Framework."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save_checkpoint(
        self, 
        workflow_id: str, 
        checkpoint_id: str, 
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save workflow checkpoint to database.
        
        Args:
            workflow_id: Unique workflow identifier
            checkpoint_id: Checkpoint identifier (e.g., "step_3")
            state_data: Workflow state (agent threads, executor state, etc.)
            metadata: Optional metadata (timestamp, user, etc.)
        """
        try:
            checkpoint = WorkflowCheckpoint(
                workflow_id=workflow_id,
                checkpoint_id=checkpoint_id,
                state_data=state_data,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            self.db.add(checkpoint)
            await self.db.commit()
            logger.info(f"Saved checkpoint {checkpoint_id} for workflow {workflow_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            await self.db.rollback()
            raise
    
    async def load_checkpoint(
        self, 
        workflow_id: str, 
        checkpoint_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Load checkpoint from database.
        
        Args:
            workflow_id: Workflow identifier
            checkpoint_id: Specific checkpoint or None for latest
            
        Returns:
            Checkpoint state data or None if not found
        """
        try:
            query = select(WorkflowCheckpoint).where(
                WorkflowCheckpoint.workflow_id == workflow_id
            )
            
            if checkpoint_id:
                query = query.where(WorkflowCheckpoint.checkpoint_id == checkpoint_id)
            else:
                query = query.order_by(WorkflowCheckpoint.created_at.desc())
            
            result = await self.db.execute(query)
            checkpoint = result.scalar_one_or_none()
            
            if checkpoint:
                logger.info(f"Loaded checkpoint {checkpoint.checkpoint_id} for workflow {workflow_id}")
                return checkpoint.state_data
            
            logger.warning(f"No checkpoint found for workflow {workflow_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            raise
    
    async def list_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """List all checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of checkpoint metadata
        """
        query = select(WorkflowCheckpoint).where(
            WorkflowCheckpoint.workflow_id == workflow_id
        ).order_by(WorkflowCheckpoint.created_at.desc())
        
        result = await self.db.execute(query)
        checkpoints = result.scalars().all()
        
        return [
            {
                "checkpoint_id": cp.checkpoint_id,
                "created_at": cp.created_at,
                "metadata": cp.metadata
            }
            for cp in checkpoints
        ]
    
    async def delete_checkpoint(self, workflow_id: str, checkpoint_id: str) -> None:
        """Delete a specific checkpoint."""
        query = select(WorkflowCheckpoint).where(
            WorkflowCheckpoint.workflow_id == workflow_id,
            WorkflowCheckpoint.checkpoint_id == checkpoint_id
        )
        result = await self.db.execute(query)
        checkpoint = result.scalar_one_or_none()
        
        if checkpoint:
            await self.db.delete(checkpoint)
            await self.db.commit()
            logger.info(f"Deleted checkpoint {checkpoint_id}")
```

**2. Add Database Model** (`backend/app/models/models.py`):

```python
from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime
from typing import Dict, Any, Optional

class WorkflowCheckpoint(SQLModel, table=True):
    """Workflow checkpoint storage."""
    __tablename__ = "workflow_checkpoints"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str = Field(index=True)
    checkpoint_id: str = Field(index=True)
    state_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**3. Integrate with WorkflowBuilder** (`backend/app/workflows/workflow_builder.py`):

```python
from app.workflows.checkpoint_storage import DatabaseCheckpointStorage

class WorkflowBuilder:
    """Enhanced workflow builder with checkpointing support."""
    
    def __init__(self, db: Session):
        self.db = db
        self.checkpoint_storage = DatabaseCheckpointStorage(db)
    
    async def build_workflow_with_checkpointing(
        self,
        workflow_config: Workflow,
        enable_checkpointing: bool = True
    ):
        """Build workflow with automatic checkpointing.
        
        Uses Agent Framework's checkpoint patterns:
        - Checkpoints created at superstep boundaries
        - Agent threads serialized for persistence
        - Executor state captured
        """
        # Build base workflow
        af_workflow = await self._build_base_workflow(workflow_config)
        
        if enable_checkpointing:
            # Add checkpoint hooks at each node
            for node in workflow_config.nodes:
                await self._add_checkpoint_hook(node, workflow_config.id)
        
        return af_workflow
    
    async def resume_workflow_from_checkpoint(
        self,
        workflow_id: str,
        checkpoint_id: Optional[str] = None
    ):
        """Resume workflow from saved checkpoint.
        
        Args:
            workflow_id: Workflow to resume
            checkpoint_id: Specific checkpoint or latest
            
        Returns:
            Resumed workflow ready for execution
        """
        # Load checkpoint state
        state = await self.checkpoint_storage.load_checkpoint(
            workflow_id, 
            checkpoint_id
        )
        
        if not state:
            raise ValueError(f"No checkpoint found for workflow {workflow_id}")
        
        # Restore workflow from state
        # - Deserialize agent threads
        # - Restore executor states
        # - Rebuild workflow graph
        restored_workflow = await self._restore_from_state(state)
        
        logger.info(f"Resumed workflow {workflow_id} from checkpoint")
        return restored_workflow
```

**4. Add Checkpoint API Endpoints** (`backend/app/api/routes/checkpoints.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional
from app.core.database import get_db
from app.workflows.checkpoint_storage import DatabaseCheckpointStorage

router = APIRouter(prefix="/api/checkpoints", tags=["checkpoints"])

@router.get("/{workflow_id}")
async def list_checkpoints(
    workflow_id: str,
    db: Session = Depends(get_db)
) -> List[dict]:
    """List all checkpoints for a workflow."""
    storage = DatabaseCheckpointStorage(db)
    return await storage.list_checkpoints(workflow_id)

@router.post("/{workflow_id}/restore")
async def restore_checkpoint(
    workflow_id: str,
    checkpoint_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Restore workflow from checkpoint."""
    from app.workflows.workflow_builder import WorkflowBuilder
    
    builder = WorkflowBuilder(db)
    workflow = await builder.resume_workflow_from_checkpoint(
        workflow_id,
        checkpoint_id
    )
    
    return {"status": "restored", "workflow_id": workflow_id}

@router.delete("/{workflow_id}/{checkpoint_id}")
async def delete_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific checkpoint."""
    storage = DatabaseCheckpointStorage(db)
    await storage.delete_checkpoint(workflow_id, checkpoint_id)
    return {"status": "deleted"}
```

##### Frontend Implementation

**1. Checkpoint Manager Component** (`frontend/src/components/CheckpointManager.tsx`):

```typescript
import React, { useState, useEffect } from 'react';
import { Button } from './ui/Button';
import { Card } from './ui/Card';

interface Checkpoint {
  checkpoint_id: string;
  created_at: string;
  metadata: Record<string, any>;
}

export const CheckpointManager: React.FC<{ workflowId: string }> = ({ workflowId }) => {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCheckpoints();
  }, [workflowId]);

  const loadCheckpoints = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/checkpoints/${workflowId}`);
      const data = await response.json();
      setCheckpoints(data);
    } catch (error) {
      console.error('Failed to load checkpoints:', error);
    } finally {
      setLoading(false);
    }
  };

  const restoreCheckpoint = async (checkpointId?: string) => {
    try {
      await fetch(`/api/checkpoints/${workflowId}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ checkpoint_id: checkpointId })
      });
      alert('Workflow restored from checkpoint');
    } catch (error) {
      console.error('Failed to restore checkpoint:', error);
    }
  };

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-4">Workflow Checkpoints</h3>
      
      <Button 
        onClick={() => restoreCheckpoint()} 
        className="mb-4"
        disabled={checkpoints.length === 0}
      >
        Restore Latest Checkpoint
      </Button>

      <div className="space-y-2">
        {loading ? (
          <p>Loading checkpoints...</p>
        ) : checkpoints.length === 0 ? (
          <p className="text-gray-500">No checkpoints available</p>
        ) : (
          checkpoints.map(cp => (
            <div key={cp.checkpoint_id} className="border p-3 rounded">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">{cp.checkpoint_id}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(cp.created_at).toLocaleString()}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => restoreCheckpoint(cp.checkpoint_id)}
                >
                  Restore
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
```

##### Testing Requirements

**Unit Tests** (`backend/tests/unit/test_checkpoint_storage.py`):
```python
import pytest
from app.workflows.checkpoint_storage import DatabaseCheckpointStorage

@pytest.mark.asyncio
async def test_save_and_load_checkpoint(db_session):
    storage = DatabaseCheckpointStorage(db_session)
    
    # Save checkpoint
    await storage.save_checkpoint(
        workflow_id="test-workflow-1",
        checkpoint_id="step-1",
        state_data={"agents": {}, "step": 1}
    )
    
    # Load checkpoint
    state = await storage.load_checkpoint("test-workflow-1", "step-1")
    assert state is not None
    assert state["step"] == 1

@pytest.mark.asyncio
async def test_list_checkpoints(db_session):
    storage = DatabaseCheckpointStorage(db_session)
    
    # Create multiple checkpoints
    for i in range(3):
        await storage.save_checkpoint(
            workflow_id="test-workflow-1",
            checkpoint_id=f"step-{i}",
            state_data={"step": i}
        )
    
    # List checkpoints
    checkpoints = await storage.list_checkpoints("test-workflow-1")
    assert len(checkpoints) == 3
```

**Integration Tests** (`backend/tests/integration/test_workflow_checkpoint.py`):
```python
@pytest.mark.asyncio
async def test_workflow_resume_from_checkpoint(db_session):
    """Test complete workflow checkpoint and resume cycle."""
    builder = WorkflowBuilder(db_session)
    
    # Create and execute workflow
    workflow = await builder.build_workflow_with_checkpointing(
        workflow_config,
        enable_checkpointing=True
    )
    
    # Execute partway
    await execute_workflow_steps(workflow, steps=2)
    
    # Simulate failure and restart
    restored_workflow = await builder.resume_workflow_from_checkpoint(
        workflow_config.id
    )
    
    # Continue execution
    result = await execute_workflow_steps(restored_workflow, remaining_steps=True)
    assert result.status == "completed"
```

##### Success Criteria

- [ ] DatabaseCheckpointStorage implemented with all methods
- [ ] WorkflowCheckpoint model added to database
- [ ] WorkflowBuilder supports checkpoint creation at superstep boundaries
- [ ] Resume from checkpoint restores full workflow state
- [ ] API endpoints functional (/checkpoints/{id}, /restore, /delete)
- [ ] Frontend CheckpointManager component working
- [ ] Unit tests passing (80%+ coverage)
- [ ] Integration tests passing
- [ ] Manual testing via DevUI successful

---

#### Task 2: Human-in-the-Loop (HITL) Integration

**Priority:** 🔴 CRITICAL  
**Effort:** 20-24 hours  
**Provider Support:** All providers

**Overview:**
Implement RequestInfoExecutor pattern for human approvals in workflows. Enable function tool approval and request/response patterns.

**Reference:** See ../agent-framework.md, search for "RequestInfoExecutor" and "ApprovalRequiredAIFunction"

##### Backend Implementation

**1. Create Request Info Executor** (`backend/app/workflows/hitl_executor.py`):

```python
"""Human-in-the-Loop executor for workflow approval points."""
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
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
    - Pause workflow execution
    - Emit approval request via WebSocket
    - Wait for human response
    - Resume with approved/rejected action
    """
    
    def __init__(self, executor_id: str, db):
        self.id = executor_id
        self.db = db
        self.pending_requests: Dict[str, HumanApprovalRequest] = {}
    
    async def request_approval(
        self,
        workflow_id: str,
        request_type: RequestType,
        data: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Request human approval and wait for response.
        
        Args:
            workflow_id: Workflow requesting approval
            request_type: Type of approval needed
            data: Request data (function call, decision options, etc.)
            timeout_seconds: Optional timeout
            
        Returns:
            Approval response from human
        """
        # Create approval request
        request = HumanApprovalRequest(
            workflow_id=workflow_id,
            request_type=request_type,
            request_data=data,
            status=ApprovalStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        
        self.pending_requests[request.id] = request
        
        # Emit WebSocket event for frontend
        await self._emit_approval_request(request)
        
        # Wait for response (with optional timeout)
        response = await self._wait_for_response(request.id, timeout_seconds)
        
        return response
    
    async def submit_approval_response(
        self,
        request_id: str,
        approved: bool,
        feedback: Optional[str] = None,
        modified_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Submit human approval response.
        
        Args:
            request_id: Request identifier
            approved: Whether approved or rejected
            feedback: Optional human feedback
            modified_data: Optional modified parameters
        """
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.response_data = {
            "approved": approved,
            "feedback": feedback,
            "modified_data": modified_data,
            "responded_at": datetime.utcnow().isoformat()
        }
        request.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Notify waiting workflow
        await self._notify_response(request_id, request.response_data)
        
        logger.info(f"Approval request {request_id} {'approved' if approved else 'rejected'}")
    
    async def _emit_approval_request(self, request: HumanApprovalRequest):
        """Emit approval request via WebSocket."""
        from app.api.websocket import manager
        
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
    
    async def _wait_for_response(
        self, 
        request_id: str, 
        timeout_seconds: Optional[int]
    ) -> Dict[str, Any]:
        """Wait for human response (implement with asyncio.wait_for if timeout needed)."""
        # Implementation depends on your async framework
        # For now, simplified version
        import asyncio
        
        max_wait = timeout_seconds or 3600  # 1 hour default
        check_interval = 1  # Check every second
        elapsed = 0
        
        while elapsed < max_wait:
            request = self.pending_requests.get(request_id)
            if request and request.status != ApprovalStatus.PENDING:
                return request.response_data
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        raise TimeoutError(f"Approval request {request_id} timed out")
    
    async def _notify_response(self, request_id: str, response_data: Dict[str, Any]):
        """Notify via WebSocket that response received."""
        from app.api.websocket import manager
        
        await manager.broadcast({
            "type": "approval_response",
            "data": {
                "request_id": request_id,
                "response": response_data
            }
        })

class ApprovalRequiredAIFunction:
    """Wrapper for AI functions requiring human approval.
    
    Compatible with Agent Framework's function tool patterns.
    """
    
    def __init__(
        self,
        function: Callable,
        executor: RequestInfoExecutor,
        workflow_id: str
    ):
        self.function = function
        self.executor = executor
        self.workflow_id = workflow_id
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
    
    async def __call__(self, *args, **kwargs):
        """Execute function with approval gate."""
        # Request approval before execution
        approval = await self.executor.request_approval(
            workflow_id=self.workflow_id,
            request_type=RequestType.FUNCTION_APPROVAL,
            data={
                "function_name": self.__name__,
                "args": args,
                "kwargs": kwargs
            }
        )
        
        if not approval["approved"]:
            raise PermissionError(f"Function {self.__name__} not approved")
        
        # Use modified parameters if provided
        modified_data = approval.get("modified_data")
        if modified_data:
            kwargs.update(modified_data)
        
        # Execute approved function
        result = await self.function(*args, **kwargs)
        
        return result
```

**2. Add Database Model** (`backend/app/models/models.py`):

```python
class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

class HumanApprovalRequest(SQLModel, table=True):
    """Human approval requests for HITL workflows."""
    __tablename__ = "human_approval_requests"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workflow_id: str = Field(index=True)
    request_type: str
    request_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    response_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

**3. Add API Endpoints** (`backend/app/api/routes/approvals.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_db
from app.workflows.hitl_executor import RequestInfoExecutor
from app.models import HumanApprovalRequest, ApprovalStatus
from pydantic import BaseModel

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

class ApprovalResponse(BaseModel):
    approved: bool
    feedback: Optional[str] = None
    modified_data: Optional[Dict[str, Any]] = None

@router.get("/pending")
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get all pending approval requests."""
    query = select(HumanApprovalRequest).where(
        HumanApprovalRequest.status == ApprovalStatus.PENDING
    ).order_by(HumanApprovalRequest.created_at.desc())
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return [
        {
            "id": req.id,
            "workflow_id": req.workflow_id,
            "request_type": req.request_type,
            "request_data": req.request_data,
            "created_at": req.created_at
        }
        for req in requests
    ]

@router.post("/{request_id}/respond")
async def respond_to_approval(
    request_id: str,
    response: ApprovalResponse,
    db: Session = Depends(get_db)
):
    """Submit approval response."""
    # Get request
    query = select(HumanApprovalRequest).where(
        HumanApprovalRequest.id == request_id
    )
    result = await db.execute(query)
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Update request
    request.status = ApprovalStatus.APPROVED if response.approved else ApprovalStatus.REJECTED
    request.response_data = response.dict()
    request.updated_at = datetime.utcnow()
    
    await db.commit()
    
    # Notify via WebSocket
    from app.api.websocket import manager
    await manager.broadcast({
        "type": "approval_response",
        "data": {
            "request_id": request_id,
            "approved": response.approved
        }
    })
    
    return {"status": "processed", "approved": response.approved}
```

##### Frontend Implementation

**1. Approval Request Panel** (`frontend/src/components/ApprovalPanel.tsx`):

```typescript
import React, { useState, useEffect } from 'react';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { Textarea } from './ui/Textarea';

interface ApprovalRequest {
  id: string;
  workflow_id: string;
  request_type: string;
  request_data: Record<string, any>;
  created_at: string;
}

export const ApprovalPanel: React.FC = () => {
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    loadPendingApprovals();
    
    // Listen for new approval requests via WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'approval_request') {
        setPendingApprovals(prev => [message.data, ...prev]);
      }
    };
    
    return () => ws.close();
  }, []);

  const loadPendingApprovals = async () => {
    try {
      const response = await fetch('/api/approvals/pending');
      const data = await response.json();
      setPendingApprovals(data);
    } catch (error) {
      console.error('Failed to load approvals:', error);
    }
  };

  const respondToApproval = async (requestId: string, approved: boolean) => {
    try {
      await fetch(`/api/approvals/${requestId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved,
          feedback: feedback || null
        })
      });
      
      // Remove from pending list
      setPendingApprovals(prev => prev.filter(req => req.id !== requestId));
      setSelectedRequest(null);
      setFeedback('');
    } catch (error) {
      console.error('Failed to respond:', error);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Pending Approvals</h2>
      
      {pendingApprovals.length === 0 ? (
        <Card className="p-4">
          <p className="text-gray-500">No pending approvals</p>
        </Card>
      ) : (
        pendingApprovals.map(request => (
          <Card key={request.id} className="p-4">
            <div className="space-y-3">
              <div>
                <p className="font-semibold">{request.request_type}</p>
                <p className="text-sm text-gray-500">
                  Workflow: {request.workflow_id}
                </p>
                <p className="text-xs text-gray-400">
                  {new Date(request.created_at).toLocaleString()}
                </p>
              </div>
              
              {request.request_type === 'function_approval' && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="font-medium">Function Call:</p>
                  <code className="text-sm">
                    {request.request_data.function_name}(
                      {JSON.stringify(request.request_data.kwargs, null, 2)}
                    )
                  </code>
                </div>
              )}
              
              <Textarea
                placeholder="Optional feedback..."
                value={selectedRequest?.id === request.id ? feedback : ''}
                onChange={(e) => {
                  setSelectedRequest(request);
                  setFeedback(e.target.value);
                }}
                className="mt-2"
              />
              
              <div className="flex gap-2">
                <Button
                  onClick={() => respondToApproval(request.id, true)}
                  variant="default"
                >
                  ✓ Approve
                </Button>
                <Button
                  onClick={() => respondToApproval(request.id, false)}
                  variant="destructive"
                >
                  ✗ Reject
                </Button>
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );
};
```

##### Testing Requirements

**Unit Tests:**
```python
@pytest.mark.asyncio
async def test_request_approval(db_session):
    executor = RequestInfoExecutor("test-executor", db_session)
    
    # Create approval request
    task = asyncio.create_task(
        executor.request_approval(
            workflow_id="test-workflow",
            request_type=RequestType.FUNCTION_APPROVAL,
            data={"function": "send_email"}
        )
    )
    
    # Simulate human response
    await asyncio.sleep(0.1)
    requests = list(executor.pending_requests.values())
    await executor.submit_approval_response(
        request_id=requests[0].id,
        approved=True
    )
    
    response = await task
    assert response["approved"] is True
```

##### Success Criteria

- [ ] RequestInfoExecutor implemented
- [ ] ApprovalRequiredAIFunction wrapper functional
- [ ] Database model for approval requests created
- [ ] API endpoints working (/pending, /respond)
- [ ] Frontend ApprovalPanel component functional
- [ ] WebSocket integration for real-time approval requests
- [ ] Unit tests passing
- [ ] Integration tests with workflow execution passing
- [ ] Manual testing via DevUI successful

---

#### Task 3: Handoff & Magentic Orchestration

**Priority:** 🔴 CRITICAL  
**Effort:** 24-30 hours  
**Provider Support:** All providers

**Overview:**
Implement advanced orchestration patterns:
- **Handoff:** Dynamic agent-to-agent control transfer
- **Magentic:** Multi-agent collaboration with plan review

**Reference:** See ../agent-framework.md, search for "Handoff" and "Magentic"

##### Backend Implementation

**Note:** This task is more complex. See the original ../agent-framework.md for complete examples of Handoff and Magentic patterns.

**Key Patterns:**

**Handoff Orchestration:**
```python
from agent_framework import WorkflowBuilder

# Create triage and specialist agents
triage_agent = await factory.create_agent(triage_config)
tech_agent = await factory.create_agent(tech_config)
sales_agent = await factory.create_agent(sales_config)

# Build handoff workflow
workflow = (
    WorkflowBuilder()
    .start_handoff_with(triage_agent)
    .with_handoff(triage_agent, tech_agent)
    .with_handoff(triage_agent, sales_agent)
    .build()
)

# Triage agent decides which specialist to hand off to
result = await workflow.run("I need help with API integration")
```

**Magentic Orchestration:**
```python
from agent_framework import MagenticBuilder

# Create specialist agents
researcher = await factory.create_agent(researcher_config)
coder = await factory.create_agent(coder_config)
reviewer = await factory.create_agent(reviewer_config)

# Build magentic workflow with plan review
workflow = (
    MagenticBuilder()
    .participants(
        researcher=researcher,
        coder=coder,
        reviewer=reviewer
    )
    .with_plan_review()  # Human reviews plan before execution
    .build()
)

result = await workflow.run("Build a REST API for user management")
```

Implementation details are in ../agent-framework.md. This task requires:
1. HandoffBuilder implementation
2. MagenticBuilder implementation
3. Plan review integration with HITL
4. UI for viewing agent collaboration

##### Success Criteria

- [ ] HandoffBuilder functional
- [ ] MagenticBuilder functional
- [ ] Plan review integrated with HITL
- [ ] Multi-agent workflows execute correctly
- [ ] Agent-to-agent handoffs work
- [ ] Plan approval UI implemented
- [ ] Tests passing
- [ ] Manual testing via DevUI successful

---

### MEDIUM PRIORITY TASKS

(Tasks 4-6: Context Providers, Observability, WorkflowViz)

Due to length constraints, see [QUICKSTART_GUIDE.md](./QUICKSTART_GUIDE.md) for patterns and ../agent-framework.md for complete implementations.

**Task 4:** Context Providers & Memory (12-16 hours)  
**Task 5:** Observability Integration (8-12 hours)  
**Task 6:** WorkflowViz Integration (6-8 hours)

---

### LOW PRIORITY TASKS

(Tasks 7-18: UI/UX improvements)

See full task list in [README.md](./README.md)

---

## Testing Requirements

### Testing Strategy

**All tests must work with any configured provider:**

```python
# tests/conftest.py
import pytest
from app.agents.agent_factory import AgentFactory

@pytest.fixture
async def agent_factory(db_session):
    """Provider-agnostic agent factory."""
    async with AgentFactory() as factory:
        yield factory
        # Factory auto-detects provider from env vars

@pytest.mark.asyncio
async def test_agent_creation(agent_factory):
    """Test works with any provider."""
    agent = await agent_factory.create_agent(test_config)
    assert agent is not None
```

### Provider-Specific Tests

Test provider-specific features when needed:

```python
@pytest.mark.skipif(
    not os.getenv("AZURE_OPENAI_ENDPOINT"),
    reason="Azure OpenAI not configured"
)
@pytest.mark.asyncio
async def test_azure_specific_feature():
    """Test Azure-specific functionality."""
    pass
```

### Coverage Requirements

- Unit tests: 80%+ coverage
- Integration tests: Critical paths covered
- Manual testing: All features tested via DevUI

---

## Success Metrics

### Technical Metrics

- [ ] All HIGH priority tasks completed
- [ ] 80%+ test coverage maintained
- [ ] No breaking changes to existing features
- [ ] All workflows execute with any configured provider
- [ ] Checkpoint recovery rate: 99%+
- [ ] HITL response time: <5 seconds
- [ ] Handoff/Magentic workflows functional

### Quality Metrics

- [ ] Code follows Microsoft Agent Framework patterns
- [ ] Multi-provider support maintained
- [ ] Documentation updated
- [ ] No lint errors
- [ ] Manual testing successful

---

## References

- **Agent Framework Docs:** [../agent-framework.md](../agent-framework.md)
- **Provider Setup:** [PROVIDER_SETUP.md](./PROVIDER_SETUP.md)
- **Quick Reference:** [QUICKSTART_GUIDE.md](./QUICKSTART_GUIDE.md)
- **Architecture:** [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)

---

**Last Updated:** October 7, 2025  
**Verified With:** Microsoft Learn MCP Tools  
**Version:** 2.0 (Multi-Provider Edition)
