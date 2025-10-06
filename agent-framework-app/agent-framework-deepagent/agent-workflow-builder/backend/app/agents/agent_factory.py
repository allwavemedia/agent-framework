"""
Agent factory for creating AI agent instances using Microsoft Agent Framework.
"""
from typing import Dict, Any, List, Union

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from app.models import Agent, AgentType
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """Factory for creating AI agent instances using Microsoft Agent Framework."""
    
    def __init__(self):
        self.chat_clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Azure OpenAI chat clients."""
        try:
            # Initialize Azure OpenAI client using correct Microsoft Agent Framework pattern
            credential = DefaultAzureCredential()
            
            # Create Azure OpenAI Chat Client
            self.azure_chat_client = AzureOpenAIChatClient(credential=credential)
            
            logger.info("Azure OpenAI chat client initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI clients: {e}")
            raise
    
    def create_agent(self, agent_config: Agent) -> ChatAgent:
        """Create an AI agent instance from configuration."""
        try:
            # Create agent using Microsoft Agent Framework pattern
            agent = self.azure_chat_client.create_agent(
                instructions=agent_config.instructions,
                name=agent_config.name
            )
            
            logger.info(f"Created agent: {agent_config.name} with type: {agent_config.agent_type}")
            return agent
                
        except Exception as e:
            logger.error(f"Error creating agent {agent_config.name}: {e}")
            raise
    
    def create_specialist_agent(self, agent_config: Agent) -> ChatAgent:
        """Create a specialist agent with enhanced instructions."""
        # Enhance instructions for specialist behavior
        specialist_instructions = f"""
        You are a specialist agent with expertise in: {agent_config.description or 'your domain'}.
        
        Core Instructions:
        {agent_config.instructions}
        
        As a specialist, you should:
        1. Provide expert-level insights and analysis
        2. Use domain-specific terminology appropriately
        3. Reference best practices and standards in your field
        4. Acknowledge limitations and suggest when to consult other specialists
        5. Be precise and thorough in your responses
        """
        
        # Create agent with enhanced instructions
        agent = self.azure_chat_client.create_agent(
            instructions=specialist_instructions,
            name=agent_config.name
        )
        
        logger.info(f"Created specialist agent: {agent_config.name}")
        return agent
    
    def create_workflow_agent(self, name: str, instructions: str) -> ChatAgent:
        """Create an agent specifically for workflow use."""
        agent = self.azure_chat_client.create_agent(
            instructions=instructions,
            name=name
        )
        
        logger.info(f"Created workflow agent: {name}")
        return agent
    
    async def run_agent(self, agent: ChatAgent, message: str) -> str:
        """Run an agent with a message and return the response."""
        try:
            # Run the agent using the correct Agent Framework pattern
            response = await agent.run(message)
            
            # Extract text from response
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, '__str__'):
                return str(response)
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise
    
    async def run_agent_streaming(self, agent: ChatAgent, message: str):
        """Run an agent with streaming response."""
        try:
            # Run the agent with streaming using the correct Agent Framework pattern
            async for update in agent.run_stream(message):
                yield update
                
        except Exception as e:
            logger.error(f"Error running agent with streaming: {e}")
            raise
    
    def get_available_clients(self) -> Dict[str, Any]:
        """Get information about available clients."""
        return {
            'azure_openai_available': hasattr(self, 'azure_chat_client'),
            'agent_framework_available': True,
        }
    
    def get_supported_agent_types(self) -> List[str]:
        """Get list of supported agent types."""
        return [
            AgentType.CHAT_AGENT.value,
            AgentType.SPECIALIST_AGENT.value,
            AgentType.TOOL_AGENT.value,
            AgentType.CUSTOM_AGENT.value
        ]