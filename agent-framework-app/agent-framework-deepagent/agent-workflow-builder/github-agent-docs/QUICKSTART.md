# Quick Start - Agent Workflow Builder

**⏱️ Time:** 5 minutes  
**Goal:** Get started building multi-provider AI agent workflows

---

## 1️⃣ Choose Your Provider (1 minute)

Pick ONE:

- **Azure OpenAI** - Enterprise/Production  
- **OpenAI Direct** - Rapid prototyping  
- **Local Models** - Development/Privacy

See [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) for detailed comparison.

---

## 2️⃣ Configure Environment (2 minutes)

### Azure OpenAI

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-01
```

### OpenAI Direct

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
```

### Local Model (Ollama)

```bash
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
```

**Full details:** [PROVIDER_SETUP.md](./PROVIDER_SETUP.md)

---

## 3️⃣ Test Configuration (1 minute)

```bash
cd backend
python -c "
from app.agents.agent_factory import AgentFactory
import asyncio

async def test():
    async with AgentFactory() as factory:
        print(f'✅ Provider: {factory.provider.value}')

asyncio.run(test())
"
```

**Expected:** `✅ Provider: azure_openai` (or openai/local)

---

## 4️⃣ Start Building (1 minute)

Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) and begin with:

**Task 1: Checkpointing & State Persistence**

- Complete implementation provided
- Backend + Frontend + Tests
- Estimated: 16-20 hours

---

## 🎯 What's Next?

### Immediate:

1. ✅ Read full [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) - 30 min
2. ✅ Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) overview - 15 min
3. ✅ Start implementing Task 1 - Begin building!

### Resources:

- **Agent Framework Docs:** `../../agent-framework.md`
- **Backend Status:** `../../docs/BACKEND_STATUS.md`
- **Full README:** [README.md](./README.md)

---

## 💡 Key Points

✅ **Backend already supports all three providers** via AgentFactory  
✅ **Auto-detection:** Local > OpenAI > Azure OpenAI priority  
✅ **Provider-agnostic code:** All implementations work with any provider  
✅ **Complete examples:** Full code for checkpointing, HITL, orchestration  

---

## 🆘 Stuck?

1. Check [FAQ.md](./FAQ.md) for common questions
2. Re-read [PROVIDER_SETUP.md](./PROVIDER_SETUP.md) for configuration issues
3. Review [README.md](./README.md) for detailed guidance

---

**Ready to build? Start with IMPLEMENTATION_GUIDE.md Task 1! 🚀**

---

**Version:** 3.0  
**Last Updated:** October 7, 2025
