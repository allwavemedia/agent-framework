"""
Observability integration for Agent Framework workflows.
Provides OpenTelemetry tracing, logging, and metrics support.
"""
from typing import Optional, Dict, Any
import os
from contextlib import contextmanager

from agent_framework.observability import setup_observability, get_tracer
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.trace.span import format_trace_id
from app.core.logging import get_logger

logger = get_logger(__name__)


class ObservabilityConfig:
    """Configuration for observability features."""
    
    def __init__(
        self,
        enable_tracing: bool = True,
        enable_metrics: bool = True,
        enable_logging: bool = True,
        service_name: str = "agent-workflow-builder",
        otel_exporter_otlp_endpoint: Optional[str] = None,
        otel_exporter_otlp_headers: Optional[str] = None,
        console_output: bool = False
    ):
        """
        Initialize observability configuration.
        
        Args:
            enable_tracing: Enable OpenTelemetry tracing
            enable_metrics: Enable metrics collection
            enable_logging: Enable structured logging
            service_name: Service name for telemetry
            otel_exporter_otlp_endpoint: OTLP endpoint for exporting telemetry
            otel_exporter_otlp_headers: Headers for OTLP exporter
            console_output: Output telemetry to console for debugging
        """
        self.enable_tracing = enable_tracing
        self.enable_metrics = enable_metrics
        self.enable_logging = enable_logging
        self.service_name = service_name
        self.otel_exporter_otlp_endpoint = otel_exporter_otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.otel_exporter_otlp_headers = otel_exporter_otlp_headers or os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
        self.console_output = console_output
    
    def to_env_vars(self) -> Dict[str, str]:
        """Convert configuration to environment variables for Agent Framework."""
        env_vars = {}
        
        if self.service_name:
            env_vars["OTEL_SERVICE_NAME"] = self.service_name
        
        if self.otel_exporter_otlp_endpoint:
            env_vars["OTEL_EXPORTER_OTLP_ENDPOINT"] = self.otel_exporter_otlp_endpoint
        
        if self.otel_exporter_otlp_headers:
            env_vars["OTEL_EXPORTER_OTLP_HEADERS"] = self.otel_exporter_otlp_headers
        
        # Enable console exporter for debugging
        if self.console_output:
            env_vars["OTEL_TRACES_EXPORTER"] = "console"
            env_vars["OTEL_METRICS_EXPORTER"] = "console"
            env_vars["OTEL_LOGS_EXPORTER"] = "console"
        
        return env_vars


class ObservabilityService:
    """Service for managing observability features in workflows."""
    
    def __init__(self, config: Optional[ObservabilityConfig] = None):
        """
        Initialize the observability service.
        
        Args:
            config: Observability configuration
        """
        self.config = config or ObservabilityConfig()
        self._initialized = False
    
    def initialize(self) -> None:
        """
        Initialize OpenTelemetry observability.
        
        This sets up tracing, metrics, and logging using the Agent Framework's
        setup_observability() function which follows OpenTelemetry standards.
        """
        if self._initialized:
            logger.warning("Observability already initialized")
            return
        
        try:
            # Set environment variables from config
            env_vars = self.config.to_env_vars()
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Use Agent Framework's setup_observability
            # This configures OpenTelemetry according to environment variables
            setup_observability()
            
            self._initialized = True
            logger.info(
                f"Observability initialized with service name: {self.config.service_name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize observability: {e}")
            raise
    
    def get_tracer(self):
        """
        Get the OpenTelemetry tracer for creating spans.
        
        Returns:
            OpenTelemetry tracer instance
        """
        if not self._initialized:
            self.initialize()
        
        return get_tracer()
    
    @contextmanager
    def trace_workflow(self, workflow_id: int, workflow_name: str):
        """
        Create a traced context for workflow execution.
        
        Args:
            workflow_id: Workflow ID
            workflow_name: Workflow name
        
        Yields:
            Span context for the workflow execution
        """
        tracer = self.get_tracer()
        
        with tracer.start_as_current_span(
            f"workflow.{workflow_name}",
            kind=SpanKind.SERVER
        ) as span:
            # Add workflow metadata as span attributes
            span.set_attribute("workflow.id", workflow_id)
            span.set_attribute("workflow.name", workflow_name)
            
            trace_id = format_trace_id(span.get_span_context().trace_id)
            logger.info(f"Started workflow trace: {trace_id}")
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                logger.error(f"Workflow trace error: {e}")
                raise
            else:
                span.set_status(Status(StatusCode.OK))
                logger.info(f"Completed workflow trace: {trace_id}")
    
    @contextmanager
    def trace_agent_execution(
        self, 
        agent_id: int, 
        agent_name: str,
        executor_id: str
    ):
        """
        Create a traced context for agent execution.
        
        Args:
            agent_id: Agent ID
            agent_name: Agent name
            executor_id: Executor ID
        
        Yields:
            Span context for the agent execution
        """
        tracer = self.get_tracer()
        
        with tracer.start_as_current_span(
            f"agent.{agent_name}",
            kind=SpanKind.INTERNAL
        ) as span:
            # Add agent metadata as span attributes
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("executor.id", executor_id)
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            else:
                span.set_status(Status(StatusCode.OK))
    
    @contextmanager
    def trace_operation(
        self, 
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Create a traced context for a generic operation.
        
        Args:
            operation_name: Name of the operation
            attributes: Optional attributes to add to the span
        
        Yields:
            Span context for the operation
        """
        tracer = self.get_tracer()
        
        with tracer.start_as_current_span(
            operation_name,
            kind=SpanKind.INTERNAL
        ) as span:
            # Add custom attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            else:
                span.set_status(Status(StatusCode.OK))
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            attributes: Optional attributes for the metric
        """
        # This would use OpenTelemetry metrics API
        # For now, log the metric
        logger.info(
            f"Metric: {metric_name}={value}",
            extra={"attributes": attributes or {}}
        )


# Global observability service instance
_observability_service: Optional[ObservabilityService] = None


def get_observability_service(
    config: Optional[ObservabilityConfig] = None
) -> ObservabilityService:
    """
    Get the global observability service instance.
    
    Args:
        config: Optional configuration (only used on first call)
    
    Returns:
        ObservabilityService instance
    """
    global _observability_service
    
    if _observability_service is None:
        _observability_service = ObservabilityService(config)
    
    return _observability_service


def initialize_observability(config: Optional[ObservabilityConfig] = None) -> None:
    """
    Initialize the global observability service.
    
    Args:
        config: Observability configuration
    """
    service = get_observability_service(config)
    service.initialize()
