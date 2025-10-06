"""
Application configuration settings.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="production", description="Environment")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./agent_workflows.db", description="Database URL")
    
    # Security
    SECRET_KEY: str = Field(description="Secret key for JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(default="gpt-4", description="Azure OpenAI deployment name")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-02-01", description="Azure OpenAI API version")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI model name")
    OPENAI_BASE_URL: Optional[str] = Field(default=None, description="Custom OpenAI base URL (for local models)")
    
    # Local Model Configuration (e.g., Ollama, LM Studio, etc.)
    LOCAL_MODEL_ENABLED: bool = Field(default=False, description="Enable local model support")
    LOCAL_MODEL_BASE_URL: Optional[str] = Field(default="http://localhost:11434/v1", description="Local model API base URL")
    LOCAL_MODEL_NAME: Optional[str] = Field(default="llama2", description="Local model name")
    
    # MCP Configuration
    MICROSOFT_LEARN_MCP_URL: str = Field(
        default="https://learn.microsoft.com/api/mcp",
        description="Microsoft Learn MCP server URL"
    )
    CONTEXT7_MCP_URL: Optional[str] = Field(default=None, description="Context7 MCP server URL")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Workflow Configuration
    MAX_WORKFLOW_EXECUTION_TIME: int = Field(default=3600, description="Maximum workflow execution time in seconds")
    MAX_CONCURRENT_WORKFLOWS: int = Field(default=10, description="Maximum concurrent workflows")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory")
    MAX_FILE_SIZE: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()