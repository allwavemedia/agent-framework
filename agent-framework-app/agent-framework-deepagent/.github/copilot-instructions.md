# GitHub Copilot Instructions for Agent Workflow Builder

This is a **Microsoft Agent Framework** application for building and executing AI agent workflows with visual design capabilities.

## Critical Development Guidelines

⚠️ **ALWAYS GROUND DEVELOPMENT WITH CURRENT INFORMATION** ⚠️
- **Use Microsoft Learn MCP tools** to verify all Agent Framework patterns and APIs
- **Use Context7 MCP tools** for library documentation and best practices  
- **Use web search** to confirm latest package versions and installation methods
- **Validate all code examples** against official Microsoft documentation before implementation

## Architecture Patterns

### Backend (FastAPI + Microsoft Agent Framework)
- **Service Layer Pattern**: All business logic in `app/services/` (AgentService, WorkflowService, ExecutionService)
- **Factory Pattern**: `AgentFactory` creates `ChatAgent` instances using `AzureOpenAIChatClient`
- **Repository Pattern**: SQLModel entities in `app/models/models.py` with typed responses
- **Builder Pattern**: `WorkflowBuilder` supports sequential, concurrent, conditional, and custom workflow patterns

### Key Integrations
- **Microsoft Agent Framework**: Use `agent-framework` package (v1.0.0b251001+, requires Python >=3.10)
- **MCP Protocol**: Tool integration via `modelcontextprotocol` in `app/services/mcp_service.py`
- **WebSocket**: Real-time execution updates through `app/api/websocket.py`
- **DevUI**: Optional development interface via `agent-framework-devui` package

## Installation & Dependencies

### Current Package Structure (As of Oct 2025)
```bash
# Full framework (recommended for development)
pip install agent-framework

# Core only (lighter dependencies)
pip install agent-framework-core

# Specific integrations
pip install agent-framework-azure-ai
pip install agent-framework-devui --pre
```

## Agent Framework Patterns

### Creating Agents
```python
# app/agents/agent_factory.py - ALWAYS use this pattern
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = self.azure_chat_client.create_agent(
    instructions=agent_config.instructions,
    name=agent_config.name
)
```

### Building Workflows
```python
# app/workflows/workflow_builder.py - Support multiple patterns
patterns = ['sequential', 'concurrent', 'conditional', 'custom']
# Use AFWorkflowBuilder with add_edge(), add_fan_out_edge(), add_fan_in_edge()
```

## Core Data Models

```python
# Essential enums and models from app/models/models.py
WorkflowStatus: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
AgentType: CHAT, SPECIALIST, WORKFLOW, CUSTOM
ExecutorType: AGENT, TOOL, CONDITIONAL, PARALLEL

# Main entities: Agent, Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution
# Pattern: Base → Create/Update → Response models for each entity
```

## Agent Framework Patterns

### Creating Agents
```python
# app/agents/agent_factory.py - ALWAYS use this pattern
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = self.azure_chat_client.create_agent(
    instructions=agent_config.instructions,
    name=agent_config.name
)
```

### Building Workflows
```python
# app/workflows/workflow_builder.py - Support multiple patterns
patterns = ['sequential', 'concurrent', 'conditional', 'custom']
# Use AFWorkflowBuilder with add_edge(), add_fan_out_edge(), add_fan_in_edge()
```

## API Route Conventions

### Standard CRUD Pattern
```python
# app/api/routes/{entity}.py
@router.get("/", response_model=List[{Entity}Response])
@router.post("/", response_model={Entity}Response, status_code=201)
@router.get("/{id}", response_model={Entity}Response)
@router.patch("/{id}", response_model={Entity}Response)
@router.delete("/{id}", status_code=204)
```

### Service Dependency Injection
```python
@router.post("/")
async def create_entity(
    data: EntityCreate,
    db: Session = Depends(get_db)
):
    service = EntityService(db)
    return await service.create_entity(data)
```

## Development Guidelines

- **Research First**: Always use MCP tools and web search to verify current patterns
- **Type Safety**: Use Pydantic/SQLModel for all data validation and serialization
- **Async First**: All service methods and API endpoints should be async
- **Error Handling**: Wrap Agent Framework calls in try/catch with proper logging
- **Dependency Management**: Use dependency injection for database sessions and services
- **Testing**: Create agents via AgentFactory, test workflows with mock executors
- **Authentication**: Use `AzureCliCredential` for Azure services (requires `az login`)

## Frontend Integration (Empty - Ready for React + TypeScript)
- Target: React Flow for visual workflow design
- State: Zustand for workflow state management  
- Communication: WebSocket for real-time execution updates
- Development: Use DevUI for rapid prototyping and testing

## MCP Tool Integration
```python
# app/services/mcp_service.py - For external tool calling
# Microsoft Learn, Context7, and custom MCP servers
# Use modelcontextprotocol package for tool discovery and execution
```

## Verification Workflow

Before implementing any Agent Framework feature:
1. **Search Microsoft Learn** for current patterns and examples
2. **Verify package versions** on PyPI and GitHub releases
3. **Test with DevUI** to validate agent/workflow behavior
4. **Cross-reference** with official documentation
5. **Use Context7** for library-specific implementation details

When working with this codebase, prioritize Microsoft Agent Framework patterns, maintain type safety, and ALWAYS verify implementation details with current documentation sources using microsoft learn mcp tools, context7 mcp tools, web search tools, and other relevant resources.