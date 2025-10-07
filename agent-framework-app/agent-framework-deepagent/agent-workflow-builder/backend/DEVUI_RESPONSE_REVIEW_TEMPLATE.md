# 📋 DevUI Response Review Template

Use this template to document responses from DevUI for analysis by GitHub Copilot or other reviewers.

---

## Test Session Information

- **Date/Time**: [Your timestamp here]
- **DevUI URL**: http://localhost:8080
- **Agent**: TestAgent
- **Model**: gpt-4o-mini

---

## Test #1: Basic Test

### Query
```
Hello! Can you introduce yourself and explain what you can help me with?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐ (1-5 stars)

### Notes
- Response time: [X seconds]
- Issues observed: [None / List any problems]
- Quality assessment: [Your thoughts]

---

## Test #2: Context Memory Test

### Query
```
My name is Alex. Please remember this. What's my name?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Did it remember the name? [Yes/No]
- Response time: [X seconds]
- Issues observed: [None / List any problems]

---

## Test #3: Workflow Design Test

### Query
```
I need to design a workflow with 3 agents: a research agent, an analysis agent, and a reporting agent. How should they work together?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Response quality: [Assessment]
- Technical accuracy: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #4: Technical Question

### Query
```
What's the difference between sequential and concurrent workflow patterns? When should I use each?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Explanation clarity: [Assessment]
- Examples provided: [Yes/No]
- Issues observed: [None / List any problems]

---

## Test #5: Complex Multi-Agent Scenario

### Query
```
Design a customer support workflow with:
- Inquiry categorization
- Routing to specialized agents
- Escalation logic
- Response generation
Give me the complete architecture.
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Completeness: [Assessment]
- Architecture quality: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #6: Real-World Problem

### Query
```
I have a data processing pipeline that needs to:
1. Collect data from APIs
2. Clean and validate
3. Analyze sentiment
4. Generate reports
5. Alert on critical issues

How would you architect this using agents?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Solution feasibility: [Assessment]
- Detail level: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #7: Debugging Scenario

### Query
```
My workflow fails intermittently with "context length exceeded" errors. What could be causing this and how do I fix it?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Diagnostic quality: [Assessment]
- Solution practicality: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #8: Best Practices

### Query
```
What are the top 5 best practices for building production-ready agent workflows?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Relevance: [Assessment]
- Completeness: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #9: Beginner Question

### Query
```
I'm new to agent frameworks. Explain how agents communicate and coordinate in the Microsoft Agent Framework.
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Beginner-friendliness: [Assessment]
- Technical accuracy: [Assessment]
- Issues observed: [None / List any problems]

---

## Test #10: Creative Problem

### Query
```
Design an AI hiring workflow that's fair, unbiased, and includes human oversight. What ethical considerations should I build in?
```

### Response
```
[PASTE AGENT'S RESPONSE HERE]
```

### Rating: ⭐⭐⭐⭐⭐

### Notes
- Ethical considerations: [Assessment]
- Practical approach: [Assessment]
- Issues observed: [None / List any problems]

---

## Overall Assessment

### Summary Statistics
- Total tests completed: X/10
- Average rating: X.X stars
- Average response time: X seconds
- Total issues found: X

### Strengths
1. [What worked well]
2. [What worked well]
3. [What worked well]

### Weaknesses
1. [What needs improvement]
2. [What needs improvement]
3. [What needs improvement]

### Critical Issues
- [ ] None found ✓
- [ ] [List any critical problems]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

---

## For GitHub Copilot Review

**Instructions**: Once you've filled this template, you can ask GitHub Copilot to:

1. **Analyze response quality**: 
   ```
   @workspace Review the agent responses in this file and assess their quality, accuracy, and helpfulness.
   ```

2. **Check technical accuracy**:
   ```
   @workspace Check if the technical information about Agent Framework in these responses is accurate.
   ```

3. **Identify patterns**:
   ```
   @workspace Analyze these responses and identify any patterns in errors, quality issues, or strengths.
   ```

4. **Compare with documentation**:
   ```
   @workspace Compare these agent responses against the Agent Framework documentation in #file:devui-doc.md
   ```

5. **Get improvement suggestions**:
   ```
   @workspace Based on these test responses, suggest improvements for the agent's instructions or configuration.
   ```

---

**Save this file as**: `devui_response_review_[DATE].md`
