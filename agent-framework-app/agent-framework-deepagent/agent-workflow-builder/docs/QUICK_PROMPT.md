# Quick GitHub Coding Agent Prompt

**🎯 MISSION:** Implement 18 Agent Framework enhancement tasks for production-ready multi-agent workflows.

## 📚 READ THESE FIRST:
1. `github-agent-docs/README.md` - Start here
2. `github-agent-docs/IMPLEMENTATION_GUIDE.md` - Complete specs (1,200 lines)
3. `github-agent-docs/PROVIDER_SETUP.md` - LLM provider setup

## 🚀 IMPLEMENTATION ORDER:

### Phase 1 (HIGH Priority - Start Here):
1. **Checkpointing & State Persistence** (16-20h) - Complete implementation in IMPLEMENTATION_GUIDE.md
2. **Human-in-the-Loop Integration** (20-24h) - Complete implementation in IMPLEMENTATION_GUIDE.md  
3. **Handoff & Orchestration** (24-30h) - Patterns provided in IMPLEMENTATION_GUIDE.md

### Phase 2 (MEDIUM Priority):
4. Context Providers & Memory (12-16h)
5. Observability Integration (8-12h)
6. WorkflowViz Integration (6-8h)

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
- [ ] Phase 1 tasks implemented
- [ ] 80%+ test coverage maintained  
- [ ] No breaking changes
- [ ] All providers work
- [ ] Tests pass: `cd backend && python -m pytest`

## 🚨 KEY RULES:
- ✅ Provider-agnostic code only
- ✅ Use Microsoft Agent Framework patterns
- ✅ Complete tasks in order (1→2→3...)
- ❌ Don't hardcode Azure-specific logic
- ❌ Don't break existing AgentFactory

**Start with:** Task 1 Checkpointing in `github-agent-docs/IMPLEMENTATION_GUIDE.md`