# GitHub Coding Agent Development Prompt

**Project:** Agent Workflow Builder - Microsoft Agent Framework Enhancement  
**Date:** October 7, 2025  
**Status:** Ready for Implementation  
**Documentation Source:** `github-agent-docs/` directory

---

## 🎯 Mission Statement

You are tasked with implementing **18 enhancement tasks** to transform the Agent Workflow Builder into a production-ready multi-agent orchestration platform using the Microsoft Agent Framework. The backend already supports multi-provider LLM integration (Azure OpenAI, OpenAI Direct, Local Models) - your job is to add the missing Agent Framework features.

---

## 📚 Essential Documentation (READ FIRST)

### Core Implementation Guides

1. **`github-agent-docs/README.md`** - Overview and navigation guide
2. **`github-agent-docs/IMPLEMENTATION_GUIDE.md`** - Complete implementation specifications (~1,200 lines)
3. **`github-agent-docs/PROVIDER_SETUP.md`** - LLM provider configuration guide (~650 lines)

### Supporting Documentation

4. **`github-agent-docs/archives/MIGRATION_SUMMARY.md`** - Multi-provider migration context
5. **`github-agent-docs/archives/MULTI_PROVIDER_ANALYSIS.md`** - Research findings and gap analysis
6. **`agent-framework.md`** - Complete Microsoft Agent Framework reference (in project root)

---

## 🏗️ Current Architecture Overview

### ✅ Already Implemented (Strong Foundation)

- **Multi-Provider AgentFactory** - Supports Azure OpenAI, OpenAI, Local models with auto-detection
- **Sequential & Concurrent Orchestration** - Basic workflow patterns implemented
- **WebSocket Streaming** - Real-time communication infrastructure
- **Comprehensive Configuration** - Environment-based provider detection
- **Test Infrastructure** - Pytest framework with API and integration tests

### 🎯 Your Implementation Target (18 Tasks)

**Phase 1: HIGH PRIORITY (Production Critical)**
1. **Checkpointing & State Persistence** (16-20 hours)
2. **Human-in-the-Loop Integration** (20-24 hours) 
3. **Handoff & Magentic Orchestration** (24-30 hours)

**Phase 2: MEDIUM PRIORITY (Enhanced Functionality)**
4. Context Providers & Memory (12-16 hours)
5. Observability Integration (8-12 hours)
6. WorkflowViz Integration (6-8 hours)

**Phase 3: LOW PRIORITY (UI/UX & Advanced)**
7-18. See IMPLEMENTATION_GUIDE.md for complete list

---

## 🔧 Technical Implementation Requirements

### Multi-Provider Pattern (CRITICAL)

All code MUST work with any of the three providers. Use this pattern:

```python
from app.agents.agent_factory import AgentFactory

# AgentFactory auto-detects provider from environment
async with AgentFactory() as factory:
    agent = await factory.create_agent(agent_config)
    response = await factory.run_agent(agent, "Hello!")
```

### Provider Auto-Detection (Already Working)

```python
class ModelProvider(str, Enum):
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai" 
    LOCAL = "local"

# Priority: Local > OpenAI > Azure OpenAI
```

### Microsoft Agent Framework Patterns

Use official Agent Framework patterns from `agent-framework.md`:

- **Checkpointing:** FileCheckpointStorage, CheckpointManager
- **HITL:** RequestInfoExecutor, ApprovalPanel
- **Orchestration:** WorkflowBuilder, handoff patterns
- **Memory:** ConversationMemory, ContextProviders

---

## 📋 Implementation Workflow

### Step 1: Setup and Configuration (30 minutes)

1. **Read Core Documentation**
   - Read `github-agent-docs/README.md` completely
   - Skim `github-agent-docs/IMPLEMENTATION_GUIDE.md` overview
   - Review provider comparison in `github-agent-docs/PROVIDER_SETUP.md`

2. **Configure LLM Provider** (Choose ONE)
   - **Local Models (Recommended for Development):** Ollama setup, no API costs
   - **OpenAI Direct:** Simple API key setup, latest models
   - **Azure OpenAI:** Enterprise setup, Azure CLI required

3. **Validate Current Setup**
   - Run existing tests: `cd backend && python -m pytest`
   - Test AgentFactory: Check `backend/app/agents/agent_factory.py` works
   - Verify WebSocket: Test streaming endpoints

### Step 2: Phase 1 Implementation (HIGH Priority)

#### Task 1: Checkpointing & State Persistence (16-20 hours)

**COMPLETE IMPLEMENTATION PROVIDED** in `github-agent-docs/IMPLEMENTATION_GUIDE.md`

**Files to Create/Modify:**
- `backend/app/workflows/checkpoint_storage.py` - DatabaseCheckpointStorage class
- `backend/app/models/__init__.py` - WorkflowCheckpoint model
- `backend/app/api/checkpoints.py` - REST endpoints
- `frontend/src/components/CheckpointPanel.tsx` - React component
- `backend/tests/test_checkpoints.py` - Test suite

**Key Features:**
- Database-backed checkpoint storage
- Workflow state serialization/deserialization
- Recovery from any checkpoint
- Real-time checkpoint UI

#### Task 2: Human-in-the-Loop Integration (20-24 hours)

**COMPLETE IMPLEMENTATION PROVIDED** in `github-agent-docs/IMPLEMENTATION_GUIDE.md`

**Files to Create/Modify:**
- `backend/app/workflows/human_input.py` - RequestInfoExecutor
- `frontend/src/components/ApprovalPanel.tsx` - Approval interface
- WebSocket integration for real-time approvals
- `backend/tests/test_human_loop.py` - Test suite

**Key Features:**
- RequestInfoExecutor for human approval
- Real-time approval interface
- WebSocket integration
- Timeout handling

#### Task 3: Handoff & Magentic Orchestration (24-30 hours)

**PATTERNS PROVIDED** in `github-agent-docs/IMPLEMENTATION_GUIDE.md`

**Files to Create/Modify:**
- `backend/app/workflows/orchestration.py` - Advanced orchestration
- Agent handoff patterns implementation
- Magentic function integration
- `backend/tests/test_orchestration.py` - Test suite

**Key Features:**
- Agent-to-agent handoffs
- Magentic function calling
- Complex workflow orchestration
- Error handling and recovery

### Step 3: Phase 2 Implementation (MEDIUM Priority)

Continue with tasks 4-6 after Phase 1 completion.

### Step 4: Testing and Validation

**Test Coverage Requirements:**
- Maintain 80%+ test coverage
- Test with multiple providers where applicable
- Integration tests for all workflows
- Manual testing via DevUI

---

## 🔑 Environment Configuration

The backend auto-detects your provider. Configure ONE of these:

### Local Models (Recommended for Development)
```bash
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=llama2
```

### OpenAI Direct
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### Azure OpenAI
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

**See `github-agent-docs/PROVIDER_SETUP.md` for complete configuration details.**

---

## 📊 Success Metrics & Validation

### Technical Metrics
- [ ] All Phase 1 tasks implemented (Checkpointing, HITL, Orchestration)
- [ ] 80%+ test coverage maintained
- [ ] No breaking changes to existing features
- [ ] All workflows execute successfully with configured provider
- [ ] Checkpoint recovery rate: 99%+
- [ ] HITL response time: <5 seconds

### Completion Criteria
- [ ] All HIGH priority features implemented and tested
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Manual testing completed via DevUI
- [ ] Code follows multi-provider patterns
- [ ] No lint errors or warnings

### Validation Commands
```bash
# Run tests
cd backend && python -m pytest

# Test specific features
python -m pytest tests/test_checkpoints.py
python -m pytest tests/test_human_loop.py
python -m pytest tests/test_orchestration.py

# Start development server
python -m uvicorn app.main:app --reload
```

---

## 🎯 Key Implementation Principles

### 1. Provider Agnostic (CRITICAL)
All code MUST work with any of the three providers. No hardcoded Azure-specific logic.

### 2. Microsoft Agent Framework First
Use official Agent Framework patterns from `agent-framework.md`. Don't reinvent patterns.

### 3. Incremental Implementation
Complete one task fully before moving to the next. Test thoroughly.

### 4. Maintain Backward Compatibility
Don't break existing AgentFactory or WorkflowBuilder functionality.

### 5. Comprehensive Testing
Test with multiple providers, maintain coverage, add integration tests.

---

## 🚨 Critical Guidelines

### DO:
- ✅ Read ALL documentation before starting implementation
- ✅ Use AgentFactory for all agent creation (provider-agnostic)
- ✅ Follow Microsoft Agent Framework patterns exactly
- ✅ Test with at least one LLM provider
- ✅ Maintain 80%+ test coverage
- ✅ Complete tasks in priority order (HIGH → MEDIUM → LOW)
- ✅ Update documentation as you implement

### DON'T:
- ❌ Hardcode provider-specific logic
- ❌ Break existing functionality
- ❌ Skip testing requirements
- ❌ Implement tasks out of priority order
- ❌ Ignore the provided implementation patterns
- ❌ Reinvent Agent Framework patterns

---

## 📁 Key File Locations

### Backend Core Files (Existing)
- `backend/app/agents/agent_factory.py` - Multi-provider agent factory ✅
- `backend/app/core/config.py` - Configuration with all env vars ✅
- `backend/app/workflows/workflow_builder.py` - Workflow builder ✅

### Frontend Core Files (Existing)
- `frontend/src/` - React TypeScript application ✅
- `frontend/src/api/` - API client implementation ✅

### Files You'll Create
- `backend/app/workflows/checkpoint_storage.py` - Task 1
- `backend/app/workflows/human_input.py` - Task 2
- `backend/app/workflows/orchestration.py` - Task 3
- `frontend/src/components/CheckpointPanel.tsx` - Task 1
- `frontend/src/components/ApprovalPanel.tsx` - Task 2
- Various test files in `backend/tests/`

---

## 🎉 Getting Started Checklist

Before you begin implementation:

- [ ] I have read `github-agent-docs/README.md` completely
- [ ] I have reviewed `github-agent-docs/IMPLEMENTATION_GUIDE.md` overview
- [ ] I have configured at least one LLM provider
- [ ] I understand the multi-provider architecture
- [ ] I have verified existing tests pass
- [ ] I understand the priority order (HIGH → MEDIUM → LOW)
- [ ] I have access to `agent-framework.md` for reference patterns
- [ ] Development environment is ready

**Start with:** `github-agent-docs/IMPLEMENTATION_GUIDE.md`, Phase 1, Task 1: Checkpointing & State Persistence

---

## 🆘 When You Need Help

1. **Re-read** the relevant section in `github-agent-docs/IMPLEMENTATION_GUIDE.md`
2. **Check** `github-agent-docs/PROVIDER_SETUP.md` for configuration issues
3. **Consult** `agent-framework.md` for Agent Framework details
4. **Review** existing code in `backend/app/agents/agent_factory.py`
5. **Run tests** to validate current functionality

---

## 🚀 Final Reminder

You have **everything you need** to implement production-grade multi-agent workflows:

- ✅ **Complete implementation specifications** (1,200+ lines)
- ✅ **Working multi-provider backend** (AgentFactory ready)
- ✅ **Provider-agnostic patterns** (tested with Microsoft Learn MCP)
- ✅ **Comprehensive test framework** (pytest + integration tests)
- ✅ **Real-time WebSocket infrastructure** (streaming ready)

**Your mission:** Transform this solid foundation into a production-ready Agent Framework application by implementing the 18 enhancement tasks, starting with Phase 1 (Checkpointing, HITL, Orchestration).

**Let's build something amazing! 🎯**

---

**Prepared by:** BMad Product Manager Agent  
**Date:** October 7, 2025  
**Status:** Ready for Implementation