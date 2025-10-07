# Orchestration Features - Task 3 Implementation

## Overview

This document describes the Handoff and Magentic orchestration features implemented for the Agent Framework Workflow Builder.

## Backend Implementation

### API Endpoints

#### Handoff State Endpoints

**List Handoffs**
```
GET /api/v1/api/orchestration/handoffs
Query params:
  - workflow_id (optional): Filter by workflow
  - limit (default: 50): Max results
  - offset (default: 0): Pagination offset
```

**Get Handoff Details**
```
GET /api/v1/api/orchestration/handoffs/{handoff_id}
```

#### Plan Review Endpoints

**List Plan Reviews**
```
GET /api/v1/api/orchestration/plan-reviews
Query params:
  - workflow_id (optional): Filter by workflow
  - status (optional): pending, approved, revised
  - limit (default: 50): Max results
  - offset (default: 0): Pagination offset
```

**Get Plan Review Details**
```
GET /api/v1/api/orchestration/plan-reviews/{review_id}
```

**Decide Plan Review**
```
POST /api/v1/api/orchestration/plan-reviews/{review_id}/decide
Body:
{
  "decision": "approve" | "revise",
  "edited_plan_text": "optional edited plan",
  "comments": "optional feedback"
}
```

### Python Modules

**HandoffBuilder** (`backend/app/workflows/orchestration.py`)
- Creates workflows with agent-to-agent control transfer
- Supports multiple handoff types: escalation, specialization, collaboration, delegation, return
- Wraps Microsoft Agent Framework patterns

**MagenticBuilder** (`backend/app/workflows/orchestration.py`)
- Wrapper for Magentic One multi-agent collaboration
- Enables plan review (human-in-the-loop)
- Supports checkpointing and progress tracking

**Database Models** (`backend/app/models/models.py`)
- `HandoffState`: Tracks agent handoffs
- `PlanReviewRequest`: Stores plan review requests and decisions

## Frontend Implementation

### Components

#### OrchestrationPanel (`frontend/src/components/OrchestrationPanel.tsx`)

**Features:**
- List view of agent-to-agent handoffs
- Auto-refresh (5-second interval)
- Color-coded handoff types
- Detail view with context data
- Agent flow visualization

**Usage:**
```tsx
<OrchestrationPanel 
  workflowId={workflowId}
  onRefresh={() => console.log('Refreshed')}
/>
```

#### PlanReviewPanel (`frontend/src/components/PlanReviewPanel.tsx`)

**Features:**
- List view of plan review requests
- Status filtering (all, pending, approved, revised)
- Inline plan editing
- Approve/Revise actions with feedback
- Review round tracking

**Usage:**
```tsx
<PlanReviewPanel 
  workflowId={workflowId}
  onReviewProcessed={() => console.log('Processed')}
/>
```

### Integration in App.tsx

The panels are integrated in the right sidebar after the ApprovalPanel:

```tsx
{workflowId && (
  <>
    <ApprovalPanel workflowId={workflowId} />
    <OrchestrationPanel workflowId={workflowId} />
    <PlanReviewPanel workflowId={workflowId} />
  </>
)}
```

## Usage Examples

### Creating a Handoff Workflow

```python
from app.workflows.orchestration import HandoffBuilder, HandoffType

# Create agents
async with AgentFactory() as factory:
    triage = await factory.create_agent(triage_config)
    tech = await factory.create_agent(tech_config)
    sales = await factory.create_agent(sales_config)
    
    # Build handoff workflow
    builder = HandoffBuilder()
    workflow = await builder.start_handoff_with(triage)\
        .with_handoff(triage, tech, "Technical questions", HandoffType.SPECIALIZATION)\
        .with_handoff(triage, sales, "Sales inquiries", HandoffType.SPECIALIZATION)\
        .build()
    
    # Execute
    result = await workflow.run("I need help with API integration")
```

### Creating a Magentic Workflow

```python
from app.workflows.orchestration import MagenticBuilder

# Create specialist agents
async with AgentFactory() as factory:
    researcher = await factory.create_agent(researcher_config)
    coder = await factory.create_agent(coder_config)
    reviewer = await factory.create_agent(reviewer_config)
    
    # Build Magentic workflow with plan review
    builder = MagenticBuilder()
    workflow = await builder.participants(
        researcher=researcher,
        coder=coder,
        reviewer=reviewer
    ).with_plan_review().build()
    
    # Execute
    result = await workflow.run("Build a REST API for user management")
```

### Reviewing Plans via UI

1. Navigate to the workflow in the UI
2. View the **Plan Reviews** panel
3. Click on a pending review to see details
4. Edit the plan if needed
5. Add comments or feedback
6. Click **Approve Plan** or **Request Revision**

## Testing

### Unit Tests
```bash
cd backend
SECRET_KEY=test-key pytest tests/unit/test_orchestration.py -v
```

### Integration Tests
```bash
cd backend
SECRET_KEY=test-key pytest tests/integration/test_orchestration_api.py -v
```

**Test Coverage:**
- 15 unit tests (builders, models, DTOs)
- 16 integration tests (API endpoints)
- All tests passing

## Architecture

### Data Flow

1. **Handoff Recording:**
   - Agent decides to handoff
   - HandoffState created in database
   - Frontend polls for updates
   - OrchestrationPanel displays handoff

2. **Plan Review:**
   - Magentic manager generates plan
   - PlanReviewRequest created in database
   - Frontend polls for new reviews
   - Human approves or requests revision
   - Decision sent to backend
   - Workflow continues or replans

### Database Schema

**handoff_states table:**
- id (primary key)
- workflow_id (indexed)
- execution_id (optional)
- current_agent_id
- previous_agent_id (optional)
- handoff_reason (optional)
- context_data (JSON)
- created_at, updated_at

**plan_review_requests table:**
- id (primary key)
- workflow_id (indexed)
- execution_id (optional)
- task_text
- facts_text
- plan_text
- round_index
- status (pending/approved/revised)
- decision (approve/revise)
- edited_plan_text (optional)
- comments (optional)
- created_at, reviewed_at

## Future Enhancements

1. **WebSocket Integration:** Real-time push notifications for handoffs and plan reviews
2. **Visualization:** Graph view of agent collaboration and handoff chains
3. **Analytics:** Metrics on handoff patterns and plan revision rates
4. **Templates:** Pre-configured handoff workflows for common patterns
5. **Advanced Filters:** Search and filter by agent, reason, date range

## References

- Implementation Guide: `github-agent-docs/IMPLEMENTATION_GUIDE.md` (lines 1073-1156)
- Core Framework: `python/packages/core/agent_framework/_workflows/_magentic.py`
- .NET Reference: `dotnet/src/Microsoft.Agents.AI.Workflows/AgentWorkflowBuilder.cs`
- Agent Framework Documentation: `agent-framework.md` (Handoff and Magentic sections)
