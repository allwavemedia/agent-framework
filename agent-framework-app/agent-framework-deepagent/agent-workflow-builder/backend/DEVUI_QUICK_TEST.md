# 🚀 DevUI Quick Test Script
**Quick Reference for Testing Agent Framework DevUI**

## Access Information
- **DevUI URL**: http://localhost:8080
- **Test Agent**: TestAgent
- **API Endpoint**: http://localhost:8080/v1/*

---

## ⚡ Quick Test Prompts (Copy & Paste Ready)

### 1. Basic Test
```
Hello! Can you introduce yourself and explain what you can help me with?
```

### 2. Context Memory Test
```
My name is Alex. Please remember this. What's my name?
```

### 3. Workflow Design Test
```
I need to design a workflow with 3 agents: a research agent, an analysis agent, and a reporting agent. How should they work together?
```

### 4. Technical Question
```
What's the difference between sequential and concurrent workflow patterns? When should I use each?
```

### 5. Complex Multi-Agent Scenario
```
Design a customer support workflow with:
- Inquiry categorization
- Routing to specialized agents
- Escalation logic
- Response generation
Give me the complete architecture.
```

### 6. Real-World Problem
```
I have a data processing pipeline that needs to:
1. Collect data from APIs
2. Clean and validate
3. Analyze sentiment
4. Generate reports
5. Alert on critical issues

How would you architect this using agents?
```

### 7. Debugging Scenario
```
My workflow fails intermittently with "context length exceeded" errors. What could be causing this and how do I fix it?
```

### 8. Best Practices
```
What are the top 5 best practices for building production-ready agent workflows?
```

### 9. Beginner Question
```
I'm new to agent frameworks. Explain how agents communicate and coordinate in the Microsoft Agent Framework.
```

### 10. Creative Problem
```
Design an AI hiring workflow that's fair, unbiased, and includes human oversight. What ethical considerations should I build in?
```

---

## ✅ Quick Validation Checklist

After each test, check:
- [ ] Response appears within 5 seconds
- [ ] Response is relevant and helpful
- [ ] Agent maintains conversation context
- [ ] UI remains responsive
- [ ] Streaming text works smoothly
- [ ] No errors in browser console

---

## 🔧 API Test Commands (PowerShell)

### Get Available Entities
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/v1/entities"
```

### Send Test Message
```powershell
$body = @{
    model = "agent-framework"
    input = "Hello from API!"
    extra_body = @{ entity_id = "agent_in-memory_testagent_1bb5eb18" }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/v1/responses" -Method POST -Body $body -ContentType "application/json"
```

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/health"
```

---

## 🎯 What to Look For

**Good Signs:**
✅ Fast response times
✅ Coherent, structured answers
✅ Remembers conversation context
✅ Handles complex queries well
✅ Graceful error handling

**Red Flags:**
❌ Long delays (>10 seconds)
❌ Incoherent or irrelevant responses
❌ Forgetting previous messages
❌ Frequent errors
❌ UI freezing or crashing

---

## 📊 Test Results Template

Copy this to track your results:

```
Test Session: [Date/Time]
Agent: TestAgent
DevUI Version: [Check about page]

Test 1 - Basic: ⭐⭐⭐⭐⭐
Test 2 - Context: ⭐⭐⭐⭐⭐
Test 3 - Workflow: ⭐⭐⭐⭐⭐
Test 4 - Technical: ⭐⭐⭐⭐⭐
Test 5 - Complex: ⭐⭐⭐⭐⭐

Issues Found:
- [List any problems]

Notes:
- [Observations]
```

---

## 🚨 Troubleshooting

**If DevUI isn't responding:**
1. Check terminal - is server still running?
2. Refresh browser page
3. Check browser console for errors
4. Verify http://localhost:8080/health returns OK

**If responses are slow:**
1. Check OpenAI API status
2. Look for rate limiting messages
3. Try simpler queries first

**If context is lost:**
1. This is expected for very long conversations
2. Start a new conversation thread
3. Be more concise in queries

---

**Pro Tip**: Open browser DevTools (F12) to monitor network requests and see any errors in real-time!
