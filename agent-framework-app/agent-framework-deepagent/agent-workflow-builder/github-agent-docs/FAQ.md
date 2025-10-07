# Frequently Asked Questions (FAQ)

**Last Updated:** October 7, 2025

---

## 🎯 Provider Selection

### Q: Which LLM provider should I use?

**A:** It depends on your needs:

| Need | Use |
|------|-----|
| **Production deployment** | Azure OpenAI |
| **Enterprise compliance** | Azure OpenAI |
| **Latest models immediately** | OpenAI Direct |
| **Rapid prototyping** | OpenAI Direct or Local |
| **Complete privacy** | Local Models |
| **Offline development** | Local Models |
| **Cost-conscious development** | Local Models (free) |

See [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) for detailed comparison.

---

### Q: Can I use multiple providers in the same project?

**A:** Yes! The backend AgentFactory auto-detects the provider based on environment variables. You can switch providers by changing your `.env` file. However, you can only use ONE provider at a time per environment.

---

### Q: Do I need to change my code when switching providers?

**A:** No! All code in IMPLEMENTATION_GUIDE.md is provider-agnostic. The AgentFactory handles provider selection automatically. Just change your environment variables and restart.

---

## 🔧 Configuration

### Q: What environment variables do I need?

**A:** Depends on your provider:

**Azure OpenAI (minimum):**
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
```

**OpenAI Direct (minimum):**
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
```

**Local Model (minimum):**
```bash
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
```

**Complete reference:** [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) → Environment Variables

---

### Q: How does provider auto-detection work?

**A:** AgentFactory checks environment variables in this priority order:

1. **Local Model** - If `LOCAL_MODEL_ENABLED=true` and `LOCAL_MODEL_BASE_URL` is set
2. **OpenAI Direct** - If `OPENAI_API_KEY` is set
3. **Azure OpenAI** - If `AZURE_OPENAI_ENDPOINT` or `AZURE_OPENAI_API_KEY` is set
4. **Default** - Falls back to Azure OpenAI (will fail if not configured)

---

### Q: I'm getting authentication errors with Azure OpenAI. What should I do?

**A:** Common solutions:

1. **Run `az login`** - Ensure you're authenticated with Azure CLI
2. **Check permissions** - Verify you have "Cognitive Services OpenAI User" role
3. **Use API key** - Set `AZURE_OPENAI_API_KEY` instead of relying on Azure CLI auth
4. **Verify endpoint** - Ensure `AZURE_OPENAI_ENDPOINT` is correct

**Full troubleshooting:** [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) → Authentication Troubleshooting

---

## 🏗️ Implementation

### Q: Where do I start implementing features?

**A:** Follow this order:

1. Read [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) - Configure your provider
2. Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Understand the tasks
3. Start with **Task 1: Checkpointing & State Persistence**
4. Move to **Task 2: Human-in-the-Loop Integration**
5. Continue with **Task 3: Handoff & Magentic Orchestration**

---

### Q: Are the code examples complete or just snippets?

**A:** Tasks 1 and 2 in IMPLEMENTATION_GUIDE.md provide **complete implementations**:

- ✅ Full Python classes with all methods
- ✅ Database models
- ✅ API endpoints
- ✅ React/TypeScript components
- ✅ Unit and integration tests
- ✅ Success criteria

Tasks 3-18 provide patterns and references to `../../agent-framework.md` for complete examples.

---

### Q: Do I need to implement all 18 tasks?

**A:** No! Prioritize based on your needs:

- **HIGH PRIORITY (Required):** Tasks 1-3 (Checkpointing, HITL, Orchestration) - ~60-74 hours
- **MEDIUM PRIORITY (Recommended):** Tasks 4-6 (Context, Observability, WorkflowViz) - ~26-36 hours
- **LOW PRIORITY (Optional):** Tasks 7-18 (UI/UX improvements) - varies

Start with HIGH priority tasks and implement others as needed.

---

### Q: Can I use the AgentFactory directly or do I need to create my own factory?

**A:** **Use the existing AgentFactory!** It's located at `backend/app/agents/agent_factory.py` and already implements multi-provider support.

```python
from app.agents.agent_factory import AgentFactory

async with AgentFactory() as factory:
    agent = await factory.create_agent(agent_config)
    response = await factory.run_agent(agent, "Hello!")
```

---

## 🧪 Testing

### Q: Do I need to test with all three providers?

**A:** **Minimum:** Test with at least one provider (whichever you configured).

**Recommended:** Test with Azure OpenAI and OpenAI Direct for production code.

**Optional:** Test with local models for development workflows.

The code should work with any provider, but some features (like function calling) may have limited support on local models.

---

### Q: How do I write provider-agnostic tests?

**A:** Use the AgentFactory fixture:

```python
@pytest.fixture
async def agent_factory(db_session):
    """Provider-agnostic agent factory."""
    async with AgentFactory() as factory:
        yield factory

@pytest.mark.asyncio
async def test_agent_creation(agent_factory):
    """Test works with any provider."""
    agent = await agent_factory.create_agent(test_config)
    assert agent is not None
```

The test will use whatever provider is configured in your `.env` file.

---

## 🚀 Deployment

### Q: Can I deploy with multiple providers?

**A:** Yes, but each deployment instance uses one provider:

- **Development:** Use local models
- **Staging:** Use OpenAI Direct
- **Production:** Use Azure OpenAI

Configure each environment with appropriate environment variables.

---

### Q: How do I switch from development (local) to production (Azure OpenAI)?

**A:** Just change environment variables:

**Development:**
```bash
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
```

**Production:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-01
```

No code changes needed!

---

## 🔍 Agent Framework

### Q: Where is the complete Agent Framework documentation?

**A:** In the repository root: `../../agent-framework.md`

This file contains the complete Microsoft Agent Framework documentation including:
- All orchestration patterns (Sequential, Concurrent, Handoff, Magentic)
- Checkpointing examples
- HITL patterns
- Context providers
- Observability setup
- Complete code examples

---

### Q: Do I need to use Microsoft Learn MCP tools?

**A:** **Optional but recommended.** The MCP tools help verify current Agent Framework APIs and patterns. All code in IMPLEMENTATION_GUIDE.md has already been verified with Microsoft Learn MCP tools.

Use MCP tools when:
- You need to verify a specific API
- You want the latest documentation
- You're implementing features not covered in IMPLEMENTATION_GUIDE.md

---

## 📊 Features

### Q: Do all Agent Framework features work with local models?

**A:** Most features work, but with some limitations:

| Feature | Azure OpenAI | OpenAI Direct | Local Models |
|---------|--------------|---------------|--------------|
| **Checkpointing** | ✅ Full | ✅ Full | ✅ Full |
| **HITL** | ✅ Full | ✅ Full | ✅ Full |
| **Handoff** | ✅ Full | ✅ Full | ✅ Full |
| **Magentic** | ✅ Full | ✅ Full | ⚠️ Depends on model |
| **Function Calling** | ✅ Full | ✅ Full | ⚠️ Model-dependent |
| **Streaming** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Context Providers** | ✅ Full | ✅ Full | ✅ Full |

Test with your specific local model to verify capabilities.

---

### Q: What's the difference between Handoff and Magentic orchestration?

**A:**

**Handoff:**
- Dynamic agent-to-agent control transfer
- One agent decides which specialist to hand off to
- Linear workflow (triage → specialist)
- Use case: Customer support routing

**Magentic:**
- Multi-agent collaboration with plan review
- Manager agent coordinates multiple specialists
- Parallel and sequential collaboration
- Use case: Complex multi-step projects

Both are covered in IMPLEMENTATION_GUIDE.md Task 3.

---

## 🆘 Troubleshooting

### Q: My code works with Azure OpenAI but fails with local models. Why?

**A:** Common reasons:

1. **Function calling not supported** - Your local model may not support function/tool calling
2. **Context length** - Local models often have shorter context windows
3. **Model quality** - Smaller models may produce lower-quality outputs
4. **API compatibility** - Ensure your local server is OpenAI-compatible

**Solution:** Test with a more capable local model (e.g., `mistral` instead of `phi`) or use cloud providers for production.

---

### Q: Where can I get more help?

**A:**

1. **Re-read documentation:**
   - [README.md](./README.md) - Overview and navigation
   - [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) - Configuration
   - [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Implementation details

2. **Check Agent Framework docs:** `../../agent-framework.md`

3. **Search GitHub issues:** https://github.com/microsoft/agent-framework/issues

4. **Use Microsoft Learn MCP tools** to verify current APIs

---

## 📚 Additional Resources

- **Backend Status:** `../../docs/BACKEND_STATUS.md`
- **Architecture:** `../../docs/Architecture.md`
- **PRD:** `../../docs/PRD.md`
- **Migration Summary:** [archives/MIGRATION_SUMMARY.md](./archives/MIGRATION_SUMMARY.md)
- **Research Findings:** [archives/MULTI_PROVIDER_ANALYSIS.md](./archives/MULTI_PROVIDER_ANALYSIS.md)

---

**Still have questions? Check [README.md](./README.md) or [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for more details!**

---

**Version:** 3.0  
**Last Updated:** October 7, 2025
