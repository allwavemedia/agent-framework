"""
API routes for observability and telemetry management.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.observability_service import (
    get_observability_service,
    initialize_observability,
    ObservabilityConfig
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/observability", tags=["observability"])


class ObservabilityConfigRequest(BaseModel):
    """Request model for observability configuration."""
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    service_name: str = "agent-workflow-builder"
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_headers: Optional[str] = None
    console_output: bool = False


class ObservabilityStatusResponse(BaseModel):
    """Response model for observability status."""
    enabled: bool
    service_name: str
    tracing_enabled: bool
    metrics_enabled: bool
    logging_enabled: bool
    configuration: Dict[str, Any]


@router.post("/initialize")
async def initialize_observability_endpoint(
    config: ObservabilityConfigRequest
):
    """
    Initialize or reconfigure observability.
    
    Args:
        config: Observability configuration
    
    Returns:
        Status of initialization
    """
    try:
        obs_config = ObservabilityConfig(
            enable_tracing=config.enable_tracing,
            enable_metrics=config.enable_metrics,
            enable_logging=config.enable_logging,
            service_name=config.service_name,
            otel_exporter_otlp_endpoint=config.otel_exporter_otlp_endpoint,
            otel_exporter_otlp_headers=config.otel_exporter_otlp_headers,
            console_output=config.console_output
        )
        
        initialize_observability(obs_config)
        
        return {
            "status": "initialized",
            "service_name": config.service_name,
            "message": "Observability has been initialized successfully"
        }
        
    except Exception as e:
        logger.error(f"Error initializing observability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ObservabilityStatusResponse)
async def get_observability_status():
    """
    Get the current observability status and configuration.
    
    Returns:
        Current observability status
    """
    try:
        service = get_observability_service()
        
        return ObservabilityStatusResponse(
            enabled=service._initialized,
            service_name=service.config.service_name,
            tracing_enabled=service.config.enable_tracing,
            metrics_enabled=service.config.enable_metrics,
            logging_enabled=service.config.enable_logging,
            configuration={
                "otel_endpoint": service.config.otel_exporter_otlp_endpoint,
                "console_output": service.config.console_output
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting observability status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for observability service."""
    return {
        "status": "healthy",
        "service": "observability",
        "features": [
            "opentelemetry_tracing",
            "workflow_tracing",
            "agent_tracing",
            "metrics_collection"
        ]
    }


@router.get("/trace-context")
async def get_trace_context():
    """
    Get information about creating and using trace contexts.
    
    Returns:
        Documentation about trace context usage
    """
    return {
        "description": "OpenTelemetry trace context for distributed tracing",
        "usage": {
            "workflow_tracing": "Use observability_service.trace_workflow(workflow_id, workflow_name)",
            "agent_tracing": "Use observability_service.trace_agent_execution(agent_id, agent_name, executor_id)",
            "custom_tracing": "Use observability_service.trace_operation(operation_name, attributes)"
        },
        "examples": {
            "python": """
from app.services.observability_service import get_observability_service

service = get_observability_service()

# Trace a workflow execution
with service.trace_workflow(workflow_id=123, workflow_name="data-pipeline"):
    # Execute workflow
    result = await execute_workflow()

# Trace an agent execution
with service.trace_agent_execution(agent_id=456, agent_name="researcher", executor_id="agent_1"):
    # Execute agent
    response = await agent.run(message)
            """
        },
        "span_attributes": {
            "workflow": ["workflow.id", "workflow.name", "workflow.status"],
            "agent": ["agent.id", "agent.name", "executor.id", "agent.type"],
            "operation": ["operation.name", "custom.attributes"]
        }
    }
