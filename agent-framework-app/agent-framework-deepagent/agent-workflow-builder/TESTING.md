# Testing Guide for Agent Workflow Builder

This guide covers how to test the Agent Workflow Builder application with different model providers.

## Prerequisites

1. **Python 3.9+** installed
2. **Node.js 18+** installed
3. One of the following model providers configured:
   - Azure OpenAI account
   - OpenAI API key
   - Local model server (e.g., Ollama)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Configure Your Model Provider

#### Option A: Azure OpenAI (Default)

Edit `.env`:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

#### Option B: OpenAI API

Edit `.env`:
```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
```

#### Option C: Local Model (Ollama)

1. Install Ollama: https://ollama.ai
2. Start Ollama and pull a model:
```bash
ollama pull llama2
```

3. Edit `.env`:
```bash
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
```

### 4. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### 5. Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

#### Run specific test suites:

```bash
# API tests
pytest tests/api/ -v

# Workflow validator tests
pytest tests/workflows/ -v

# Integration tests
pytest tests/integration/ -v
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if your backend is not on localhost:8000:
```bash
VITE_API_URL=http://localhost:8000
```

### 3. Start the Frontend

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Testing Workflow

### 1. Create an Agent

1. Open http://localhost:8000/docs (FastAPI Swagger UI)
2. Use the POST `/api/agents/` endpoint to create an agent:

```json
{
  "name": "Test Agent",
  "description": "A test agent",
  "agent_type": "CHAT_AGENT",
  "instructions": "You are a helpful assistant.",
  "model_config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "tools": []
}
```

### 2. Use the Workflow Builder UI

1. Open http://localhost:5173
2. Click "New Workflow" to create a new workflow
3. Drag nodes from the left panel onto the canvas:
   - Start Node (required)
   - Agent Node (connect to your created agent)
   - End Node (required)
4. Connect nodes by dragging from one node's handle to another
5. Click "Save" to save your workflow
6. Click "Validate" to check for errors
7. Click "Execute" to run the workflow

### 3. Monitor Execution

The right panel shows:
- Execution status (Ready/Running/Completed/Failed)
- WebSocket connection status
- Validation results
- Node properties when selected
- Available agents

### 4. Test API Endpoints

Using curl or the Swagger UI at http://localhost:8000/docs:

```bash
# List agents
curl http://localhost:8000/api/agents/

# Create workflow
curl -X POST http://localhost:8000/api/workflows/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Workflow", "version": "1.0.0"}'

# Validate workflow
curl -X POST http://localhost:8000/api/workflows/1/validate

# Execute workflow
curl -X POST http://localhost:8000/api/executions/ \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": 1, "input_data": {"message": "Hello"}}'
```

## Testing Different Model Providers

### Test Azure OpenAI

```bash
# In .env
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key

# Restart backend
uvicorn app.main:app --reload
```

### Test OpenAI API

```bash
# In .env
OPENAI_API_KEY=your-key

# Restart backend
uvicorn app.main:app --reload
```

### Test Local Model

```bash
# Start Ollama
ollama serve

# In another terminal
ollama pull llama2

# In .env
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2

# Restart backend
uvicorn app.main:app --reload
```

## Troubleshooting

### Backend Issues

**"No module named X"**
- Solution: `pip install -r requirements.txt`

**"AgentFactory not initialized"**
- Solution: Check your model provider configuration in `.env`

**"Connection refused"**
- Solution: Ensure the backend is running on http://localhost:8000

### Frontend Issues

**"Failed to fetch"**
- Solution: Check VITE_API_URL in `.env` and ensure backend is running

**"WebSocket connection failed"**
- Solution: WebSocket requires a running backend with valid workflow execution

**Drag and drop not working**
- Solution: Ensure you're dragging from the node palette on the left

## Known Limitations

1. **Execution requires valid credentials**: Workflows won't execute without proper API keys or model access
2. **WebSocket requires saved workflow**: Real-time monitoring only works after saving a workflow
3. **Limited error handling**: Some edge cases may not be handled gracefully

## API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

For issues or questions, please check:
1. The logs in the terminal running the backend
2. The browser console for frontend errors
3. The test output for specific failures
