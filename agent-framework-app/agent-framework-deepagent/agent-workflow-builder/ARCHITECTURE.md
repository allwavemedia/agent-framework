# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent Workflow Builder                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                            Frontend Layer                            │
├─────────────────────────────────────────────────────────────────────┤
│  React + TypeScript + Vite                                          │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Node Palette │  │ Workflow     │  │ Execution    │             │
│  │ (Drag Source)│  │ Canvas       │  │ Monitor      │             │
│  │              │  │ (React Flow) │  │ (Real-Time)  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                       │
│  ┌────────────────────────────────────────────────────┐             │
│  │ Custom Hooks (useAgents, useWorkflow, etc.)        │             │
│  └────────────────────────────────────────────────────┘             │
│                                                                       │
│  ┌────────────────────────────────────────────────────┐             │
│  │ API Client (REST) + WebSocket Client               │             │
│  └────────────────────────────────────────────────────┘             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP/WS
┌───────────────────────────┴─────────────────────────────────────────┐
│                            Backend Layer                             │
├─────────────────────────────────────────────────────────────────────┤
│  FastAPI + SQLModel                                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                    API Routes                             │       │
│  │  /api/agents      /api/workflows    /api/executions      │       │
│  │  /api/ws          /api/mcp                                │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                  Service Layer                            │       │
│  │  AgentService  WorkflowService  ExecutionService         │       │
│  │  MCPService    WebSocketManager                           │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                  Workflow Components                      │       │
│  │  WorkflowValidator  WorkflowVisualizer  WorkflowExecutor │       │
│  │  WorkflowBuilder                                          │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                   AgentFactory                            │       │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐           │       │
│  │  │  Azure    │  │  OpenAI   │  │  Local    │           │       │
│  │  │  OpenAI   │  │  Client   │  │  Model    │           │       │
│  │  │  Client   │  │           │  │  Client   │           │       │
│  │  └───────────┘  └───────────┘  └───────────┘           │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                   Data Models                             │       │
│  │  Agent  Workflow  WorkflowNode  WorkflowEdge             │       │
│  │  WorkflowExecution                                        │       │
│  └──────────────────────────────────────────────────────────┘       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────────┐
│                        Database Layer                                │
├─────────────────────────────────────────────────────────────────────┤
│  SQLite (Dev) / PostgreSQL (Prod)                                   │
│                                                                       │
│  Tables: agents, workflows, workflow_nodes, workflow_edges,         │
│          workflow_executions                                         │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────┬─────────────────────────────────────────┐
│                   AI Model Providers                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Azure       │  │  OpenAI      │  │  Local       │             │
│  │  OpenAI      │  │  API         │  │  Models      │             │
│  │              │  │              │  │              │             │
│  │  - GPT-4     │  │  - GPT-4     │  │  - Ollama    │             │
│  │  - GPT-3.5   │  │  - GPT-3.5   │  │  - LM Studio │             │
│  │              │  │              │  │  - LocalAI   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Workflow Creation Flow

```
User Action (Drag Node) 
    ↓
Frontend: NodePalette.onDragStart()
    ↓
Frontend: App.onDrop() → Create Node
    ↓
Frontend: apiClient.createNode()
    ↓
Backend: POST /api/workflows/nodes
    ↓
Backend: WorkflowService.create_node()
    ↓
Backend: Save to Database
    ↓
Frontend: Update UI
```

### Workflow Execution Flow

```
User Clicks "Execute"
    ↓
Frontend: handleExecute() → apiClient.createExecution()
    ↓
Backend: POST /api/executions/
    ↓
Backend: ExecutionService.create_execution()
    ↓
Backend: WorkflowExecutor.execute_async()
    ↓
Backend: WebSocket Broadcasting (Real-Time)
    ↓
Frontend: useWebSocket() receives events
    ↓
Frontend: Update Execution Monitor
```

### Agent Creation Flow (Multi-Provider)

```
User Creates Agent
    ↓
Backend: AgentService.create_agent()
    ↓
Backend: AgentFactory._detect_provider()
    ↓
┌────────────┬────────────┬────────────┐
│ Azure      │ OpenAI     │ Local      │
│ OpenAI     │ API        │ Model      │
└────────────┴────────────┴────────────┘
    ↓            ↓            ↓
Initialize Client
    ↓
Create ChatAgent
    ↓
Return Agent Instance
```

## Component Interaction

### Frontend Components

```
App (Main Container)
│
├─ NodePalette
│  ├─ Node Type List
│  ├─ Agent Selector
│  └─ Drag Handlers
│
├─ ReactFlow Canvas
│  ├─ Nodes (Visual Elements)
│  ├─ Edges (Connections)
│  ├─ Controls (Zoom, Pan)
│  ├─ MiniMap
│  └─ Background
│
└─ ExecutionMonitor
   ├─ Status Display
   ├─ Validation Results
   ├─ Node Properties
   └─ Agent List
```

### Backend Services

```
API Layer
│
├─ AgentService
│  ├─ CRUD Operations
│  └─ Agent Testing
│
├─ WorkflowService
│  ├─ Workflow CRUD
│  ├─ Node Management
│  ├─ Edge Management
│  ├─ Validation
│  └─ Visualization
│
├─ ExecutionService
│  ├─ Execution Management
│  ├─ Status Tracking
│  └─ Result Storage
│
├─ WebSocketManager
│  ├─ Connection Management
│  ├─ Message Broadcasting
│  └─ Execution Streaming
│
└─ MCPService
   ├─ Tool Discovery
   └─ Tool Integration
```

## Request/Response Flow

### Example: Create and Execute Workflow

```
1. Create Agent
   POST /api/agents/
   Body: {name, instructions, type}
   Response: {id, ...}

2. Create Workflow
   POST /api/workflows/
   Body: {name, version}
   Response: {id, ...}

3. Add Nodes
   POST /api/workflows/nodes
   Body: {workflow_id, name, type, config}
   Response: {id, ...}

4. Add Edges
   POST /api/workflows/edges
   Body: {workflow_id, source, target}
   Response: {id, ...}

5. Validate
   POST /api/workflows/{id}/validate
   Response: {valid, errors[], warnings[]}

6. Execute
   POST /api/executions/
   Body: {workflow_id, input_data}
   Response: {id, status}

7. Monitor (WebSocket)
   WS /api/ws/execution/{id}
   Receives: {type: "execution_event", data: {...}}
```

## Technology Stack

### Frontend
- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS
- **Workflow Canvas**: React Flow (@xyflow/react)
- **HTTP Client**: Fetch API
- **WebSocket**: Native WebSocket API

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **ORM**: SQLModel
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI Framework**: Microsoft Agent Framework
- **WebSocket**: FastAPI WebSocket
- **Testing**: pytest, pytest-asyncio

### AI Providers
- **Azure OpenAI**: Azure SDK + DefaultAzureCredential
- **OpenAI**: OpenAI Python SDK
- **Local Models**: OpenAI-compatible API (Ollama, LM Studio)

## Security Considerations

```
Frontend
├─ Environment Variables (.env)
│  └─ API_URL only
│
Backend
├─ Environment Variables (.env)
│  ├─ SECRET_KEY (JWT signing)
│  ├─ API Keys (Azure/OpenAI)
│  └─ Database credentials
│
Authentication
├─ API Key authentication
└─ Azure AD integration (optional)

Best Practices
├─ Never commit .env files
├─ Use strong SECRET_KEY
├─ Rotate API keys regularly
└─ Use HTTPS in production
```

## Deployment Options

```
Development
├─ Backend: uvicorn --reload
└─ Frontend: npm run dev

Production
├─ Backend: gunicorn + uvicorn workers
├─ Frontend: npm run build → nginx
├─ Database: PostgreSQL
└─ Reverse Proxy: nginx/traefik
```

## Monitoring & Observability

```
Logging
├─ Backend: structlog + Rich
└─ Frontend: Console + Error Boundaries

Metrics
├─ Execution times
├─ Success/failure rates
└─ Node execution stats

Real-Time Updates
├─ WebSocket connection status
├─ Execution progress
└─ Validation results
```
