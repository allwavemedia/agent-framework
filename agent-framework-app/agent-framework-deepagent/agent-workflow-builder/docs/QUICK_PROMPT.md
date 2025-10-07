# Quick GitHub Coding Agent Prompt - Updated Oct 7, 2025

**🎯 MISSION:** Complete remaining Agent Framework tasks after recent backend implementation.

## 📚 READ THESE FIRST:
1. `github-agent-docs/README.md` - Start here
2. `github-agent-docs/IMPLEMENTATION_GUIDE.md` - Complete specs (1,200 lines)
3. `github-agent-docs/PROVIDER_SETUP.md` - LLM provider setup

## ✅ RECENT PROGRESS (Oct 7, 2025):
- ✅ **Task 1 Backend:** Checkpointing & State Persistence - COMPLETE
- ✅ **Task 2 Backend:** Human-in-the-Loop Integration - COMPLETE  
- ❌ **Frontend Components:** CheckpointPanel.tsx, ApprovalPanel.tsx - MISSING
- ❌ **Dependencies:** Backend requires `pip install -r requirements.txt`

## 🚀 REMAINING TASKS (Priority Order):

### IMMEDIATE (HIGH Priority - Start Here):
1. **Install Dependencies** (30 min) - `cd backend && pip install -r requirements.txt`
2. **Frontend Components** (8-12h) - CheckpointPanel.tsx, ApprovalPanel.tsx for Tasks 1 & 2
3. **Handoff & Orchestration** (24-30h) - Task 3 backend implementation

### Phase 2 (MEDIUM Priority):
1. Context Providers & Memory (12-16h)
2. Observability Integration (8-12h)
3. WorkflowViz Integration (6-8h)

## 🔧 CRITICAL REQUIREMENTS:

**Multi-Provider Pattern (Use This):**

```python
from app.agents.agent_factory import AgentFactory

async with AgentFactory() as factory:  # Auto-detects provider
    agent = await factory.create_agent(agent_config)
    response = await factory.run_agent(agent, "Hello!")
```

**LLM Provider Setup (Choose ONE):**

- Local Models: `LOCAL_MODEL_ENABLED=true`
- OpenAI: `OPENAI_API_KEY=sk-...`
- Azure: `AZURE_OPENAI_ENDPOINT=https://...`

## ✅ SUCCESS CRITERIA:

- [ ] **Dependencies installed** (`pip install -r requirements.txt`)
- [ ] **Frontend components complete** (CheckpointPanel, ApprovalPanel)
- [ ] **Task 3 implemented** (Handoff & Orchestration)
- [ ] 80%+ test coverage maintained  
- [ ] No breaking changes
- [ ] All providers work
- [ ] Tests pass: `cd backend && python -m pytest`

## 🚨 KEY RULES:

- ✅ Provider-agnostic code only
- ✅ Use Microsoft Agent Framework patterns
- ✅ Complete tasks in priority order
- ❌ Don't hardcode Azure-specific logic
- ❌ Don't break existing AgentFactory

## 🎯 IMMEDIATE NEXT STEPS:

1. **Install dependencies first:** `cd backend && pip install -r requirements.txt`
2. **Create frontend components:** CheckpointPanel.tsx, ApprovalPanel.tsx  
3. **Implement Task 3:** Handoff & Orchestration patterns from IMPLEMENTATION_GUIDE.md

**Backend APIs are ready** - Tasks 1 & 2 backends complete, just need frontend!