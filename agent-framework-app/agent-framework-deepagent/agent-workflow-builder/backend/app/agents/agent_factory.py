"""
Agent factory for creating AI agent instances using Microsoft Agent Framework.
"""
from typing import Dict, Any, List, Union, Optional
from contextlib import asynccontextmanager

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from app.models import Agent, AgentType
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """Factory for creating AI agent instances using Microsoft Agent Framework.
    
    This factory uses async context management patterns as recommended by the
    Microsoft Agent Framework documentation. Clients should be used with async context
    managers to ensure proper resource cleanup.
    """
    
    def __init__(self):
        self.chat_clients = {}
        self._credential: Optional[DefaultAzureCredential] = None
        self._azure_chat_client: Optional[AzureOpenAIChatClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_clients()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_clients()
        return False
    
    async def _initialize_clients(self) -> None:
        """Initialize Azure OpenAI chat clients with async context management."""
        try:
            # Initialize Azure credential
            self._credential = DefaultAzureCredential()
            
            # Create Azure OpenAI Chat Client
            # Note: AzureOpenAIChatClient can be used directly without async context
            # but we store it for potential cleanup
            self._azure_chat_client = AzureOpenAIChatClient(credential=self._credential)
            
            logger.info("Azure OpenAI chat client initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI clients: {e}")
            raise
    
    async def _cleanup_clients(self) -> None:
        """Clean up clients and resources."""
        try:
            # Clean up any resources if needed
            self._azure_chat_client = None
            self._credential = None
            logger.info("Azure OpenAI chat clients cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up clients: {e}")
    
    async def create_agent(self, agent_config: Agent) -> ChatAgent:
        """Create an AI agent instance from configuration.
        
        Args:
            agent_config: Agent configuration containing name, instructions, etc.
            
        Returns:
            ChatAgent instance ready to use
            
        Raises:
            Exception: If agent creation fails
        """
        try:
            if self._azure_chat_client is None:
                raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
            
            # Create agent using Microsoft Agent Framework pattern
            agent = self._azure_chat_client.create_agent(
                instructions=agent_config.instructions,
                name=agent_config.name
            )
            
            logger.info(f"Created agent: {agent_config.name} with type: {agent_config.agent_type}")
            return agent
                
        except Exception as e:
            logger.error(f"Error creating agent {agent_config.name}: {e}")
            raise
    
    async def create_specialist_agent(self, agent_config: Agent) -> ChatAgent:
        """Create a specialist agent with enhanced instructions.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            ChatAgent configured as a specialist
        """
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
        
        if self._azure_chat_client is None:
            raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
        
        # Create agent with enhanced instructions
        agent = self._azure_chat_client.create_agent(
            instructions=specialist_instructions,
            name=agent_config.name
        )
        
        logger.info(f"Created specialist agent: {agent_config.name}")
        return agent
    
    async def create_workflow_agent(self, name: str, instructions: str) -> ChatAgent:
        """Create an agent specifically for workflow use.
        
        Args:
            name: Agent name
            instructions: Agent instructions
            
        Returns:
            ChatAgent for workflow execution
        """
        if self._azure_chat_client is None:
            raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
        
        agent = self._azure_chat_client.create_agent(
            instructions=instructions,
            name=name
        )
        
        logger.info(f"Created workflow agent: {name}")
        return agent
    
    async def run_agent(self, agent: ChatAgent, message: str) -> str:
        """Run an agent with a message and return the response.
        
        Args:
            agent: ChatAgent instance to run
            message: User message to process
            
        Returns:
            Agent response as string
        """
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
        """Run an agent with streaming response.
        
        Args:
            agent: ChatAgent instance to run
            message: User message to process
            
        Yields:
            Response updates as they arrive
        """
        try:
            # Run the agent with streaming using the correct Agent Framework pattern
            async for update in agent.run_stream(message):
                yield update
                
        except Exception as e:
            logger.error(f"Error running agent with streaming: {e}")
            raise
    
    def get_available_clients(self) -> Dict[str, Any]:
        """Get information about available clients.
        
        Returns:
            Dict with client availability information
        """
        return {
            'azure_openai_available': self._azure_chat_client is not None,
            'agent_framework_available': True,
        }
    
    def get_supported_agent_types(self) -> List[str]:
        """Get list of supported agent types.
        
        Returns:
            List of supported agent type values
        """
        return [
            AgentType.CHAT_AGENT.value,
            AgentType.SPECIALIST_AGENT.value,
            AgentType.TOOL_AGENT.value,
            AgentType.CUSTOM_AGENT.value
        ]
    
    @property
    def azure_chat_client(self) -> Optional[AzureOpenAIChatClient]:
        """Get the Azure chat client for backward compatibility.
        
        Returns:
            AzureOpenAIChatClient instance or None
        """
        return self._azure_chat_client