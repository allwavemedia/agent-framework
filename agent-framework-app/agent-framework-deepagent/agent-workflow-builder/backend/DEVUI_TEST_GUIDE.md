# DevUI Testing Guide
## Agent Workflow Builder - Test Scenarios

**DevUI Access**: http://localhost:8080  
**Test Agent**: TestAgent (currently running)

---

## 🎯 Test Scenario 1: Basic Conversation Flow

### Test 1.1: Simple Greeting
**Purpose**: Verify basic agent responsiveness

**Your Input**:
```
Hello! Can you introduce yourself?
```

**Expected Response**: 
- Agent should respond with introduction as a test agent for Agent Workflow Builder
- Response should be clear and coherent

---

### Test 1.2: Multi-turn Conversation
**Purpose**: Test conversation context retention

**Your Input** (sequence):
1. ```
   My name is Alex. I'm testing the Agent Workflow Builder.
   ```

2. ```
   Do you remember my name?
   ```

3. ```
   What am I testing?
   ```

**Expected Response**: 
- Agent should remember your name (Alex)
- Agent should recall you're testing the Agent Workflow Builder
- Demonstrates conversation memory

---

## 🧪 Test Scenario 2: Complex Reasoning

### Test 2.1: Problem Solving
**Your Input**:
```
I have 3 agents that need to work together:
1. A research agent that gathers information
2. An analysis agent that processes data
3. A reporting agent that creates summaries

How should I design a workflow for these agents?
```

**Expected Response**:
- Structured workflow recommendations
- Sequential or parallel processing suggestions
- Clear reasoning about agent coordination

---

### Test 2.2: Technical Explanation
**Your Input**:
```
Explain the difference between sequential and concurrent workflow patterns in agent systems. Give me examples of when to use each.
```

**Expected Response**:
- Clear explanation of both patterns
- Practical examples
- Use case recommendations

---

## 🔧 Test Scenario 3: Agent Framework Features

### Test 3.1: Tool/Function Understanding
**Your Input**:
```
What kinds of tools can agents in the Microsoft Agent Framework use? Can you give me examples of common tool types?
```

**Expected Response**:
- List of tool capabilities
- Examples of common tools (API calls, data retrieval, calculations, etc.)
- How tools integrate with agents

---

### Test 3.2: Workflow Design Query
**Your Input**:
```
I want to create a workflow that:
1. Takes a user question
2. Searches a knowledge base
3. If information is found, formats a response
4. If not found, asks for clarification

What workflow pattern should I use? Draw this out for me conceptually.
```

**Expected Response**:
- Conditional workflow pattern recommendation
- Step-by-step breakdown
- Decision points and branching logic

---

## 🐛 Test Scenario 4: Error Handling & Edge Cases

### Test 4.1: Ambiguous Request
**Your Input**:
```
Make it better.
```

**Expected Response**:
- Agent should ask for clarification
- Should handle vague input gracefully

---

### Test 4.2: Complex Multi-part Question
**Your Input**:
```
Can you help me understand:
1. How agents communicate with each other
2. What happens when an agent fails
3. How to implement retry logic
4. Best practices for agent orchestration
5. Security considerations for multi-agent systems
```

**Expected Response**:
- Structured response addressing each point
- Clear organization
- Comprehensive coverage

---

## 📊 Test Scenario 5: Real-world Use Cases

### Test 5.1: Customer Support Workflow
**Your Input**:
```
Design a multi-agent workflow for customer support that:
- Receives customer inquiries
- Categorizes the inquiry type
- Routes to specialized agents (billing, technical, general)
- Escalates complex issues
- Generates response drafts
- Tracks resolution status

What agents would I need and how should they interact?
```

**Expected Response**:
- Complete workflow design
- Agent roles and responsibilities
- Communication patterns
- Error handling approach

---

### Test 5.2: Data Processing Pipeline
**Your Input**:
```
I need to process customer feedback data:
1. Collect feedback from multiple sources
2. Clean and normalize the text
3. Perform sentiment analysis
4. Extract key topics
5. Generate summary reports
6. Flag urgent issues for immediate attention

How would you architect this as an agent workflow?
```

**Expected Response**:
- Pipeline architecture
- Agent assignments for each step
- Data flow between agents
- Parallel vs sequential processing decisions

---

## 🎨 Test Scenario 6: Creative & Reasoning Tasks

### Test 6.1: Creative Problem Solving
**Your Input**:
```
A company wants to automate their hiring process using AI agents. They want to be fair, unbiased, and efficient. Design an agent workflow that balances automation with human oversight. What ethical considerations should be built in?
```

**Expected Response**:
- Thoughtful workflow design
- Ethical considerations
- Human-in-the-loop checkpoints
- Bias mitigation strategies

---

### Test 6.2: Comparison Task
**Your Input**:
```
Compare these three approaches for building an agent workflow:
A) Single powerful general-purpose agent
B) Multiple specialized agents with strict workflows
C) Hybrid approach with flexible agent coordination

What are the pros and cons of each? When would you use each approach?
```

**Expected Response**:
- Detailed comparison
- Clear pros/cons for each
- Use case recommendations
- Trade-off analysis

---

## 🧩 Test Scenario 7: Technical Deep Dive

### Test 7.1: Implementation Details
**Your Input**:
```
I'm implementing a workflow with these requirements:
- Maximum 5 second response time
- Handle up to 100 concurrent requests
- Graceful degradation if external APIs fail
- Comprehensive logging and tracing
- Cost optimization for API calls

What technical considerations should I keep in mind for each requirement?
```

**Expected Response**:
- Technical recommendations for each requirement
- Implementation strategies
- Potential pitfalls to avoid

---

### Test 7.2: Debugging Scenario
**Your Input**:
```
My workflow is failing intermittently. Here's what I observe:
- Works fine for simple inputs
- Fails on complex multi-step tasks
- Error messages mention "context length exceeded"
- Some agents timeout after 30 seconds

What debugging steps should I take and what might be causing these issues?
```

**Expected Response**:
- Systematic debugging approach
- Root cause analysis
- Potential solutions for each issue

---

## 📝 Test Scenario 8: Documentation & Best Practices

### Test 8.1: Best Practices Query
**Your Input**:
```
What are the top 10 best practices for building production-ready agent workflows? Include both technical and operational considerations.
```

**Expected Response**:
- Numbered list of best practices
- Mix of technical and operational advice
- Practical examples

---

### Test 8.2: Getting Started Guide
**Your Input**:
```
I'm brand new to agent frameworks. Can you give me a step-by-step beginner's guide to building my first agent workflow? Assume I know programming but not agent systems.
```

**Expected Response**:
- Beginner-friendly explanation
- Step-by-step instructions
- Example to follow

---

## 🔍 Validation Checklist

After testing, verify:

- [ ] **Response Time**: Responses arrive within reasonable time (< 5 seconds for simple queries)
- [ ] **Coherence**: Responses are well-structured and make sense
- [ ] **Context Retention**: Agent remembers earlier conversation parts
- [ ] **Error Handling**: Graceful handling of unclear or problematic inputs
- [ ] **Formatting**: Proper use of markdown, lists, code blocks where appropriate
- [ ] **Completeness**: Multi-part questions get multi-part answers
- [ ] **Technical Accuracy**: Information about Agent Framework is correct
- [ ] **UI Responsiveness**: DevUI interface remains responsive during interactions
- [ ] **Streaming**: Text appears progressively (streaming response)
- [ ] **Visual Elements**: Check if DevUI shows message history, typing indicators, etc.

---

## 🐞 Known Issues to Watch For

Monitor for these potential problems:

1. **Token Limits**: Very long conversations may hit context limits
2. **API Rate Limits**: Rapid successive queries might trigger rate limiting
3. **Timeout Issues**: Complex queries taking too long to respond
4. **Memory Issues**: Agent forgetting earlier context
5. **UI Freezing**: Browser becoming unresponsive during long responses
6. **WebSocket Disconnections**: Connection drops during streaming

---

## 📊 Performance Metrics to Track

While testing, note:

- **First Response Time**: Time to first token
- **Complete Response Time**: Total time to finish response
- **Response Quality**: Subjective rating (1-5)
- **Context Accuracy**: Did it remember previous inputs?
- **Error Rate**: How many queries resulted in errors?

---

## 🎯 Success Criteria

The test is successful if:

✅ Agent responds to all test scenarios  
✅ Maintains context across conversation  
✅ Provides relevant, helpful responses  
✅ DevUI interface remains stable  
✅ Streaming functionality works smoothly  
✅ No major errors or crashes  
✅ Response times are acceptable  

---

## 🚀 Next Steps After Testing

Once you've completed these tests:

1. **Document Issues**: Note any problems encountered
2. **Test Custom Agents**: Try creating your own agent configurations
3. **Test Workflows**: If workflow support is available, test workflow execution
4. **API Testing**: Use the API endpoints directly (see below)
5. **Performance Testing**: Try stress testing with multiple rapid queries

---

## 🔧 API Testing (Optional)

You can also test the DevUI API directly:

### Get Entities List
```powershell
curl http://localhost:8080/v1/entities
```

### Send Message to Agent
```powershell
$body = @{
    model = "agent-framework"
    input = "Hello, this is an API test!"
    extra_body = @{
        entity_id = "agent_in-memory_testagent_1bb5eb18"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/v1/responses" -Method POST -Body $body -ContentType "application/json"
```

### Health Check
```powershell
curl http://localhost:8080/health
```

---

## 💡 Tips for Effective Testing

1. **Start Simple**: Begin with basic queries before complex ones
2. **Take Notes**: Document interesting responses or issues
3. **Vary Input Style**: Try questions, commands, scenarios
4. **Test Boundaries**: Push the limits to find breaking points
5. **Check UI Elements**: Don't just focus on responses, check the entire interface
6. **Monitor Console**: Keep browser developer console open for errors
7. **Compare with Expectations**: Does behavior match documentation?

---

## 📞 Support & Resources

- **DevUI Documentation**: See `devui-doc.md`
- **Agent Framework Docs**: https://github.com/microsoft/agent-framework
- **API Reference**: http://localhost:8080/docs (if available)
- **Backend Logs**: Check terminal where DevUI is running

---

**Happy Testing! 🎉**

*Last Updated: October 6, 2025*
