"""
Agent factory for creating AI agent instances using Microsoft Agent Framework.

Supports multiple model providers:
- Azure OpenAI
- OpenAI
- Local models (Ollama, LM Studio, etc.)
"""
from typing import Dict, Any, List, Union, Optional
from contextlib import asynccontextmanager
from enum import Enum

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient
from agent_framework.exceptions import ServiceInitializationError
from azure.identity import DefaultAzureCredential

from app.models import Agent, AgentType
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ModelProvider(str, Enum):
    """Supported model providers."""
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    LOCAL = "local"


class AgentFactory:
    """Factory for creating AI agent instances using Microsoft Agent Framework.
    
    This factory uses async context management patterns as recommended by the
    Microsoft Agent Framework documentation. Clients should be used with async context
    managers to ensure proper resource cleanup.
    
    Supports multiple model providers:
    - Azure OpenAI (via Azure credentials)
    - OpenAI (via API key)
    - Local models (Ollama, LM Studio, etc.)
    """
    
    def __init__(self, provider: Optional[ModelProvider] = None):
        self.chat_clients = {}
        self._credential: Optional[DefaultAzureCredential] = None
        self._azure_chat_client: Optional[AzureOpenAIChatClient] = None
        self._openai_chat_client: Optional[OpenAIChatClient] = None
        self._local_chat_client: Optional[OpenAIChatClient] = None
        
        # Determine provider based on configuration if not explicitly set
        if provider is None:
            provider = self._detect_provider()
        
        self.provider = provider
        logger.info(f"AgentFactory initialized with provider: {provider.value}")
    
    def _detect_provider(self) -> ModelProvider:
        """Detect which model provider to use based on configuration."""
        # Priority: Local > OpenAI > Azure OpenAI
        if settings.LOCAL_MODEL_ENABLED and settings.LOCAL_MODEL_BASE_URL:
            return ModelProvider.LOCAL
        elif settings.OPENAI_API_KEY:
            return ModelProvider.OPENAI
        elif settings.AZURE_OPENAI_ENDPOINT or settings.AZURE_OPENAI_API_KEY:
            return ModelProvider.AZURE_OPENAI
        else:
            # Default to Azure OpenAI
            logger.warning("No model provider configured, defaulting to Azure OpenAI")
            return ModelProvider.AZURE_OPENAI
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_clients()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_clients()
        return False
    
    async def _initialize_clients(self) -> None:
        """Initialize chat clients based on the selected provider."""
        try:
            if self.provider == ModelProvider.AZURE_OPENAI:
                await self._initialize_azure_client()
            elif self.provider == ModelProvider.OPENAI:
                await self._initialize_openai_client()
            elif self.provider == ModelProvider.LOCAL:
                await self._initialize_local_client()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            logger.info(f"{self.provider.value} chat client initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing chat clients: {e}")
            raise
    
    async def _initialize_azure_client(self) -> None:
        """Initialize Azure OpenAI chat client."""
        self._credential = DefaultAzureCredential()
        self._azure_chat_client = AzureOpenAIChatClient(credential=self._credential)
    
    async def _initialize_openai_client(self) -> None:
        """Initialize OpenAI chat client."""
        if not settings.OPENAI_API_KEY:
            raise ServiceInitializationError("OPENAI_API_KEY is required for OpenAI provider")
        
        # Create OpenAI client
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        
        self._openai_chat_client = OpenAIChatClient(
            client=openai_client,
            model=settings.OPENAI_MODEL
        )
    
    async def _initialize_local_client(self) -> None:
        """Initialize local model client (OpenAI-compatible API)."""
        if not settings.LOCAL_MODEL_BASE_URL:
            raise ServiceInitializationError("LOCAL_MODEL_BASE_URL is required for local provider")
        
        # Create local model client (OpenAI-compatible)
        from openai import AsyncOpenAI
        local_client = AsyncOpenAI(
            api_key="not-needed",  # Local models typically don't require API keys
            base_url=settings.LOCAL_MODEL_BASE_URL
        )
        
        self._local_chat_client = OpenAIChatClient(
            client=local_client,
            model=settings.LOCAL_MODEL_NAME or "llama2"
        )
    
    async def _cleanup_clients(self) -> None:
        """Clean up clients and resources."""
        try:
            # Clean up any resources if needed
            self._azure_chat_client = None
            self._openai_chat_client = None
            self._local_chat_client = None
            self._credential = None
            logger.info(f"{self.provider.value} chat clients cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up clients: {e}")
    
    def _get_active_client(self):
        """Get the active chat client based on provider."""
        if self.provider == ModelProvider.AZURE_OPENAI:
            return self._azure_chat_client
        elif self.provider == ModelProvider.OPENAI:
            return self._openai_chat_client
        elif self.provider == ModelProvider.LOCAL:
            return self._local_chat_client
        return None
    
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
            chat_client = self._get_active_client()
            if chat_client is None:
                raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
            
            # Create agent using Microsoft Agent Framework pattern
            agent = chat_client.create_agent(
                instructions=agent_config.instructions,
                name=agent_config.name
            )
            
            logger.info(f"Created agent: {agent_config.name} with type: {agent_config.agent_type} using {self.provider.value}")
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
        
        chat_client = self._get_active_client()
        if chat_client is None:
            raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
        
        # Create agent with enhanced instructions
        agent = chat_client.create_agent(
            instructions=specialist_instructions,
            name=agent_config.name
        )
        
        logger.info(f"Created specialist agent: {agent_config.name} using {self.provider.value}")
        return agent
    
    async def create_workflow_agent(self, name: str, instructions: str) -> ChatAgent:
        """Create an agent specifically for workflow use.
        
        Args:
            name: Agent name
            instructions: Agent instructions
            
        Returns:
            ChatAgent for workflow execution
        """
        chat_client = self._get_active_client()
        if chat_client is None:
            raise RuntimeError("AgentFactory not initialized. Use 'async with AgentFactory()' pattern.")
        
        agent = chat_client.create_agent(
            instructions=instructions,
            name=name
        )
        
        logger.info(f"Created workflow agent: {name} using {self.provider.value}")
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
            'current_provider': self.provider.value,
            'azure_openai_available': self._azure_chat_client is not None,
            'openai_available': self._openai_chat_client is not None,
            'local_model_available': self._local_chat_client is not None,
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
    
    @property
    def openai_chat_client(self) -> Optional[OpenAIChatClient]:
        """Get the OpenAI chat client.
        
        Returns:
            OpenAIChatClient instance or None
        """
        return self._openai_chat_client
    
    @property
    def local_chat_client(self) -> Optional[OpenAIChatClient]:
        """Get the local model chat client.
        
        Returns:
            OpenAIChatClient instance or None
        """
        return self._local_chat_client