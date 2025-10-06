# Quick Start Guide

Get the Agent Workflow Builder up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- One of: Azure OpenAI account, OpenAI API key, or Ollama installed

## Option 1: Quick Start with OpenAI (Easiest)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
DATABASE_URL=sqlite:///./agent_workflows.db
EOF

# Start the server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the dev server
npm run dev
```

### 3. Open Your Browser

Visit http://localhost:5173 and start building workflows!

## Option 2: Quick Start with Local Model (Free)

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama and pull a model
ollama pull llama2
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
DATABASE_URL=sqlite:///./agent_workflows.db
EOF

uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

### 4. Open Your Browser

Visit http://localhost:5173 and start building workflows!

## Option 3: Quick Start with Azure OpenAI

### 1. Get Azure OpenAI Credentials

From Azure Portal → Azure OpenAI → Keys and Endpoint

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
DATABASE_URL=sqlite:///./agent_workflows.db
EOF

uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

### 4. Open Your Browser

Visit http://localhost:5173 and start building workflows!

## Creating Your First Workflow

### Using the UI (Recommended)

1. **Open** http://localhost:5173
2. **Click** "New Workflow"
3. **Enter** a workflow name
4. **Drag** a "Start Node" from the left palette onto the canvas
5. **Drag** an "Agent Node" onto the canvas
6. **Drag** an "End Node" onto the canvas
7. **Connect** the nodes by dragging from one node to another
8. **Click** "Save"
9. **Click** "Validate" to check for errors
10. **Click** "Execute" to run your workflow!

### Using the API

1. **Create an agent:**
```bash
curl -X POST http://localhost:8000/api/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Agent",
    "agent_type": "CHAT_AGENT",
    "instructions": "You are a helpful assistant.",
    "model_config": {}
  }'
```

2. **Create a workflow:**
```bash
curl -X POST http://localhost:8000/api/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workflow",
    "version": "1.0.0"
  }'
```

3. **View API docs** at http://localhost:8000/docs

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify your .env file is configured
- Run: `pip install -r requirements.txt`

### Frontend won't start
- Check if port 5173 is available
- Run: `npm install`
- Verify VITE_API_URL in .env

### Can't create agents
- Check your model provider credentials
- View backend logs for errors
- Test your API key separately

### Execution fails
- Ensure you saved the workflow first
- Check validation for errors
- Verify your model provider is configured correctly

## What's Next?

- Read [TESTING.md](./TESTING.md) for detailed testing instructions
- Read [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md) for technical details
- Check the API docs at http://localhost:8000/docs
- Build more complex workflows with multiple agents!

## Need Help?

- Check the logs in your terminal
- View the browser console for frontend errors
- Test individual API endpoints at http://localhost:8000/docs

## Features Included

✅ Multiple model providers (Azure OpenAI, OpenAI, Local)  
✅ Visual workflow builder with drag-and-drop  
✅ Real-time execution monitoring  
✅ Workflow validation  
✅ API integration  
✅ Comprehensive testing  

Happy workflow building! 🚀
