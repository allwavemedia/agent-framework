"""
Test DevUI Launch Script

This script demonstrates launching DevUI programmatically with the Agent Workflow Builder backend.
It uses in-memory registration to test the DevUI interface without requiring directory-based discovery.
"""

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from agent_framework.devui import serve

def main():
    """Launch DevUI with a simple test agent."""
    
    # Create a simple chat client using OpenAI
    # This will use OpenAI API key from environment variables (OPENAI_API_KEY)
    try:
        chat_client = OpenAIChatClient()
        
        # Create a test agent with Agent Framework-specific knowledge
        test_agent = ChatAgent(
            name="TestAgent",
            chat_client=chat_client,
            instructions="""You are an expert assistant for the Microsoft Agent Framework and Agent Workflow Builder.

**Your Expertise:**
- Microsoft Agent Framework (Python & .NET)
- Agent creation using ChatAgent, SpecialistAgent
- Workflow orchestration with WorkflowBuilder
- Azure OpenAI and OpenAI integration
- Agent tools and function calling
- Multi-agent coordination patterns

**When answering:**
1. Provide Agent Framework-specific guidance using actual classes and APIs
2. Include Python code examples using agent_framework imports
3. Reference official patterns: sequential, concurrent, conditional workflows
4. Mention relevant classes: ChatAgent, AzureOpenAIChatClient, OpenAIChatClient, WorkflowBuilder
5. Explain practical implementation with code snippets
6. Consider production best practices for agent systems

**Example Response Style:**
```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

agent = ChatAgent(
    name="MyAgent",
    chat_client=OpenAIChatClient(),
    instructions="Your instructions here"
)
```

Be practical, code-focused, and framework-specific in your responses."""
        )
        
        print("🚀 Launching DevUI with test agent...")
        print("📋 Agent Name: TestAgent")
        print("🌐 DevUI will open at: http://localhost:8080")
        print("📡 API available at: http://localhost:8080/v1/*")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Launch DevUI with the test agent
        serve(
            entities=[test_agent],
            port=8080,
            host="127.0.0.1",
            auto_open=True,
            ui_enabled=True,
            tracing_enabled=False
        )
        
    except Exception as e:
        print(f"❌ Error launching DevUI: {e}")
        print("\nPlease ensure:")
        print("1. OpenAI API key is set in environment variables (OPENAI_API_KEY)")
        print("2. The .env file is properly configured")
        print("3. agent-framework-devui is installed")
        raise

if __name__ == "__main__":
    main()
