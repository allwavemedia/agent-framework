# LLM Provider Setup Guide

**Last Updated:** October 7, 2025  
**Verified With:** Microsoft Learn MCP Tools

---

## Overview

The Agent Workflow Builder supports three LLM providers through the Microsoft Agent Framework. This guide covers setup, configuration, and troubleshooting for each provider.

**Backend Support:** The AgentFactory already implements multi-provider support with automatic detection.

---

## Table of Contents

1. [Provider Comparison](#provider-comparison)
2. [Azure OpenAI Setup](#azure-openai-setup)
3. [OpenAI Direct Setup](#openai-direct-setup)
4. [Local Model Setup](#local-model-setup)
5. [Environment Variables](#environment-variables)
6. [Authentication Troubleshooting](#authentication-troubleshooting)
7. [Testing Your Configuration](#testing-your-configuration)

---

## Provider Comparison

| Feature | Azure OpenAI | OpenAI Direct | Local Models |
|---------|--------------|---------------|--------------|
| **Best For** | Production, Enterprise | Prototyping, Latest models | Development, Privacy |
| **Cost** | Pay-as-you-go (Azure) | Pay-as-you-go (OpenAI) | Free (hardware only) |
| **Latency** | Low (Azure regions) | Medium | Very Low (localhost) |
| **Setup Complexity** | Medium | Low | Medium |
| **Authentication** | Azure CLI / API Key | API Key | None |
| **Latest Models** | Delayed | Immediate | Varies |
| **Data Privacy** | Azure compliance | OpenAI terms | Complete (on-prem) |
| **Function Calling** | ✅ Full | ✅ Full | ⚠️ Model-dependent |
| **Streaming** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Offline Support** | ❌ No | ❌ No | ✅ Yes |

---

## Azure OpenAI Setup

### Prerequisites

1. Azure subscription with access to Azure OpenAI Service
2. Azure CLI installed and authenticated (`az login`)
3. Azure OpenAI resource created with deployed model

### Step 1: Create Azure OpenAI Resource

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name agent-workflow-rg --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name agent-workflow-openai \
  --resource-group agent-workflow-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

### Step 2: Deploy a Model

Via Azure Portal:
1. Navigate to your Azure OpenAI resource
2. Go to "Deployments" blade
3. Click "Create new deployment"
4. Select model (e.g., `gpt-4`)
5. Name your deployment (e.g., `gpt-4-deployment`)

Or via CLI:

```bash
az cognitiveservices account deployment create \
  --name agent-workflow-openai \
  --resource-group agent-workflow-rg \
  --deployment-name gpt-4-deployment \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 1
```

### Step 3: Get Connection Details

```bash
# Get endpoint
az cognitiveservices account show \
  --name agent-workflow-openai \
  --resource-group agent-workflow-rg \
  --query properties.endpoint \
  --output tsv

# Get API key (optional if using Azure CLI auth)
az cognitiveservices account keys list \
  --name agent-workflow-openai \
  --resource-group agent-workflow-rg \
  --query key1 \
  --output tsv
```

### Step 4: Configure Environment Variables

Create `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-01

# Optional: Use API key instead of Azure CLI auth
# AZURE_OPENAI_API_KEY=your-api-key
```

### Step 5: Verify Azure CLI Authentication

```bash
# Ensure you're logged in
az account show

# If not logged in
az login

# Verify access to the resource
az cognitiveservices account show \
  --name agent-workflow-openai \
  --resource-group agent-workflow-rg
```

### Azure OpenAI Code Example

```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
import os

# Using Azure CLI authentication (recommended)
agent = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    credential=AzureCliCredential(),
    model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
).create_agent(
    instructions="You are a helpful assistant",
    name="AzureAgent"
)

# Or using API key
from agent_framework.azure import AzureOpenAIChatClient

agent = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    model_id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
).create_agent(
    instructions="You are a helpful assistant",
    name="AzureAgent"
)
```

---

## OpenAI Direct Setup

### Prerequisites

1. OpenAI account (https://platform.openai.com)
2. API key with credits

### Step 1: Create API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name your key (e.g., "agent-workflow-builder")
4. Copy the key (you won't see it again!)
5. Add credits if needed: https://platform.openai.com/account/billing

### Step 2: Configure Environment Variables

Create `.env` file:

```bash
# OpenAI Direct Configuration
OPENAI_API_KEY=sk-proj-...your-key-here...
OPENAI_MODEL=gpt-4

# Optional: Use custom base URL
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### Step 3: Verify API Key

```bash
# Test with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### OpenAI Direct Code Example

```python
from agent_framework.openai import OpenAIChatClient
import os

# Using OpenAI Direct
agent = OpenAIChatClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_id=os.getenv("OPENAI_MODEL", "gpt-4")
).create_agent(
    instructions="You are a helpful assistant",
    name="OpenAIAgent"
)

# Using AsyncOpenAI client (for more control)
from openai import AsyncOpenAI
from agent_framework.openai import OpenAIChatClient

openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = OpenAIChatClient(
    client=openai_client,
    model=os.getenv("OPENAI_MODEL", "gpt-4")
).create_agent(
    instructions="You are a helpful assistant",
    name="OpenAIAgent"
)
```

---

## Local Model Setup

### Prerequisites

1. Local model runtime (Ollama, LM Studio, or OpenAI-compatible server)
2. Sufficient GPU/RAM for your chosen model

### Option 1: Ollama (Recommended for Development)

#### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

#### Pull a Model

```bash
# Pull Llama 2 (7B)
ollama pull llama2

# Or pull other models
ollama pull codellama    # Code-focused
ollama pull mistral      # Fast inference
ollama pull phi          # Lightweight

# List available models
ollama list
```

#### Start Ollama Server

```bash
# Server typically starts automatically on port 11434
# Verify it's running
curl http://localhost:11434/api/tags
```

### Option 2: LM Studio

1. Download from https://lmstudio.ai
2. Install and launch LM Studio
3. Download a model from the model library
4. Start the local server (usually port 1234)
5. Enable OpenAI-compatible API endpoint

### Option 3: vLLM or Text Generation WebUI

See their respective documentation for setup.

### Configure Environment Variables

Create `.env` file:

```bash
# Local Model Configuration
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1  # Ollama default
LOCAL_MODEL_NAME=llama2

# For LM Studio, use:
# LOCAL_MODEL_BASE_URL=http://localhost:1234/v1
# LOCAL_MODEL_NAME=TheBloke/Llama-2-7B-Chat-GGUF
```

### Local Model Code Example

```python
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
import os

# Create OpenAI-compatible client pointing to local server
local_client = AsyncOpenAI(
    api_key="not-needed",  # Local models don't need API keys
    base_url=os.getenv("LOCAL_MODEL_BASE_URL", "http://localhost:11434/v1")
)

# Create agent
agent = OpenAIChatClient(
    client=local_client,
    model=os.getenv("LOCAL_MODEL_NAME", "llama2")
).create_agent(
    instructions="You are a helpful assistant",
    name="LocalAgent"
)
```

### Local Model Limitations

⚠️ **Important Considerations:**

1. **Function Calling:** Not all local models support function calling. Test thoroughly.
2. **Performance:** Depends on your hardware (GPU/CPU/RAM)
3. **Model Quality:** Smaller models may have lower quality outputs
4. **Context Length:** Local models often have shorter context windows
5. **Streaming:** Most support streaming, but verify with your model

---

## Environment Variables

### Complete .env Example

```bash
# ============================================
# LLM Provider Configuration
# Choose ONE provider by setting its variables
# ============================================

# Database
DATABASE_URL=sqlite:///./agent_workflows.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENVIRONMENT=production

# ============================================
# Option 1: Azure OpenAI (Enterprise)
# ============================================
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
# AZURE_OPENAI_API_VERSION=2024-02-01
# AZURE_OPENAI_API_KEY=your-key-here  # Optional if using Azure CLI

# ============================================
# Option 2: OpenAI Direct (Rapid Development)
# ============================================
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4

# ============================================
# Option 3: Local Model (Development/Privacy)
# ============================================
# LOCAL_MODEL_ENABLED=true
# LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
# LOCAL_MODEL_NAME=llama2

# ============================================
# Observability (Optional)
# ============================================
# OTEL_ENABLED=true
# AZURE_MONITOR_CONNECTION_STRING=InstrumentationKey=...  # For Azure deployments

# ============================================
# CORS Configuration
# ============================================
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO

# ============================================
# Workflow Configuration
# ============================================
MAX_WORKFLOW_EXECUTION_TIME=3600
MAX_CONCURRENT_WORKFLOWS=10

# ============================================
# File Storage
# ============================================
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

### Provider Auto-Detection

The `AgentFactory` automatically detects which provider to use based on this priority:

1. **Local Model** - If `LOCAL_MODEL_ENABLED=true` and `LOCAL_MODEL_BASE_URL` is set
2. **OpenAI Direct** - If `OPENAI_API_KEY` is set
3. **Azure OpenAI** - If `AZURE_OPENAI_ENDPOINT` or `AZURE_OPENAI_API_KEY` is set
4. **Default** - Falls back to Azure OpenAI (will fail if not configured)

You can also explicitly specify the provider:

```python
from app.agents.agent_factory import AgentFactory, ModelProvider

# Force a specific provider
async with AgentFactory(provider=ModelProvider.OPENAI) as factory:
    agent = await factory.create_agent(agent_config)
```

---

## Authentication Troubleshooting

### Azure OpenAI Issues

**Problem:** `DefaultAzureCredentialError: no credentials available`

**Solutions:**
1. Run `az login` and authenticate
2. Verify account: `az account show`
3. Or use API key instead: Set `AZURE_OPENAI_API_KEY`

**Problem:** `AuthorizationFailed` or `Access Denied`

**Solutions:**
1. Verify you have "Cognitive Services OpenAI User" role
2. Check resource group permissions
3. Ensure subscription is active

**Problem:** `ResourceNotFound`

**Solutions:**
1. Verify endpoint URL is correct
2. Check deployment name matches
3. Ensure resource exists: `az cognitiveservices account show`

### OpenAI Direct Issues

**Problem:** `AuthenticationError: Incorrect API key`

**Solutions:**
1. Verify API key in environment: `echo $OPENAI_API_KEY`
2. Check for extra spaces or quotes
3. Regenerate key if needed

**Problem:** `RateLimitError`

**Solutions:**
1. Check your usage limits: https://platform.openai.com/account/limits
2. Add credits to your account
3. Implement retry logic with exponential backoff

**Problem:** `ModelNotFoundError`

**Solutions:**
1. Verify model name (case-sensitive)
2. Check available models: `GET https://api.openai.com/v1/models`
3. Ensure you have access to the model

### Local Model Issues

**Problem:** `Connection refused` or `Cannot connect`

**Solutions:**
1. Verify server is running: `curl http://localhost:11434/api/tags`
2. Check port number matches configuration
3. Restart the local model server

**Problem:** `Model not found`

**Solutions:**
1. List available models: `ollama list`
2. Pull the model: `ollama pull llama2`
3. Verify model name matches exactly

**Problem:** Poor quality outputs

**Solutions:**
1. Use a larger/better model (e.g., `mistral` instead of `phi`)
2. Adjust temperature and other parameters
3. Provide more detailed instructions
4. Consider using cloud providers for production

---

## Testing Your Configuration

### Quick Test Script

Create `test_provider.py`:

```python
import asyncio
import os
from app.agents.agent_factory import AgentFactory
from app.models import Agent, AgentType

async def test_provider():
    """Test the configured LLM provider."""
    
    # Create test agent configuration
    agent_config = Agent(
        name="TestAgent",
        agent_type=AgentType.CHAT_AGENT,
        instructions="You are a helpful assistant. Respond with 'Hello!' to test messages.",
        description="Test agent"
    )
    
    try:
        async with AgentFactory() as factory:
            print(f"✅ Provider detected: {factory.provider.value}")
            print(f"📊 Available clients: {factory.get_available_clients()}")
            
            # Create agent
            agent = await factory.create_agent(agent_config)
            print("✅ Agent created successfully")
            
            # Test agent
            response = await factory.run_agent(agent, "Hello, can you hear me?")
            print(f"✅ Agent response: {response}")
            
            print("\n🎉 Configuration test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_provider())
```

Run the test:

```bash
cd backend
python test_provider.py
```

### Expected Output

**Success:**
```
✅ Provider detected: openai
📊 Available clients: {'current_provider': 'openai', ...}
✅ Agent created successfully
✅ Agent response: Hello! Yes, I can hear you...
🎉 Configuration test passed!
```

**Failure:**
```
❌ Configuration test failed: No API key provided...
```

### Manual Testing with DevUI

The Agent Framework includes a DevUI for testing:

```bash
# Install DevUI
pip install agent-framework-devui --pre

# Run DevUI
cd backend
python -m agent_framework_devui
```

Then test your agents interactively in the web interface.

---

## Provider-Specific Best Practices

### Azure OpenAI

✅ **Do:**
- Use Azure CLI authentication for development
- Use Managed Identity for production deployments
- Monitor costs in Azure Portal
- Set up alerts for quota limits
- Use private endpoints for sensitive data

❌ **Don't:**
- Hardcode API keys in code
- Commit credentials to git
- Share API keys across environments
- Exceed rate limits without handling errors

### OpenAI Direct

✅ **Do:**
- Rotate API keys regularly
- Monitor usage dashboard
- Set spending limits
- Use separate keys for dev/prod
- Implement retry logic

❌ **Don't:**
- Expose API keys in client-side code
- Share API keys publicly
- Ignore rate limit errors
- Skip error handling

### Local Models

✅ **Do:**
- Test with multiple models for your use case
- Monitor GPU/CPU usage
- Use quantized models for faster inference
- Set appropriate context windows
- Verify function calling support

❌ **Don't:**
- Use local models for production without testing
- Assume all models support all features
- Ignore model quality differences
- Run without sufficient resources

---

## Next Steps

1. ✅ Choose and configure your provider
2. ✅ Run the test script to verify configuration
3. ✅ Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) to start implementing features
4. ✅ Bookmark [QUICKSTART_GUIDE.md](./QUICKSTART_GUIDE.md) for quick reference

---

**Last Updated:** October 7, 2025  
**Verified With:** Microsoft Learn MCP Tools
