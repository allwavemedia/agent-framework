"""
Unit tests for Observability integration.
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from app.services.observability_service import (
    ObservabilityConfig,
    ObservabilityService,
    get_observability_service,
    initialize_observability
)


def test_observability_config_default():
    """Test default observability configuration."""
    config = ObservabilityConfig()
    
    assert config.enable_tracing is True
    assert config.enable_metrics is True
    assert config.enable_logging is True
    assert config.service_name == "agent-workflow-builder"
    assert config.console_output is False


def test_observability_config_custom():
    """Test custom observability configuration."""
    config = ObservabilityConfig(
        enable_tracing=False,
        service_name="test-service",
        otel_exporter_otlp_endpoint="http://localhost:4317",
        console_output=True
    )
    
    assert config.enable_tracing is False
    assert config.service_name == "test-service"
    assert config.otel_exporter_otlp_endpoint == "http://localhost:4317"
    assert config.console_output is True


def test_observability_config_to_env_vars():
    """Test converting configuration to environment variables."""
    config = ObservabilityConfig(
        service_name="test-service",
        otel_exporter_otlp_endpoint="http://localhost:4317",
        console_output=True
    )
    
    env_vars = config.to_env_vars()
    
    assert env_vars["OTEL_SERVICE_NAME"] == "test-service"
    assert env_vars["OTEL_EXPORTER_OTLP_ENDPOINT"] == "http://localhost:4317"
    assert "OTEL_TRACES_EXPORTER" in env_vars
    assert env_vars["OTEL_TRACES_EXPORTER"] == "console"


def test_observability_service_creation():
    """Test creating observability service."""
    config = ObservabilityConfig(service_name="test")
    service = ObservabilityService(config)
    
    assert service.config.service_name == "test"
    assert service._initialized is False


@patch('app.services.observability_service.setup_observability')
def test_observability_service_initialize(mock_setup):
    """Test initializing observability service."""
    config = ObservabilityConfig(service_name="test")
    service = ObservabilityService(config)
    
    service.initialize()
    
    assert service._initialized is True
    mock_setup.assert_called_once()


@patch('app.services.observability_service.setup_observability')
def test_observability_service_initialize_idempotent(mock_setup):
    """Test that initialize is idempotent."""
    service = ObservabilityService()
    
    service.initialize()
    service.initialize()  # Should not call setup again
    
    assert mock_setup.call_count == 1


@patch('app.services.observability_service.setup_observability')
@patch('app.services.observability_service.get_tracer')
def test_observability_service_get_tracer(mock_get_tracer, mock_setup):
    """Test getting tracer from observability service."""
    mock_tracer = MagicMock()
    mock_get_tracer.return_value = mock_tracer
    
    service = ObservabilityService()
    tracer = service.get_tracer()
    
    assert tracer == mock_tracer
    assert service._initialized is True


@patch('app.services.observability_service.setup_observability')
@patch('app.services.observability_service.get_tracer')
def test_trace_workflow_context(mock_get_tracer, mock_setup):
    """Test workflow tracing context manager."""
    mock_tracer = MagicMock()
    mock_span = MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    mock_get_tracer.return_value = mock_tracer
    
    service = ObservabilityService()
    
    with service.trace_workflow(workflow_id=123, workflow_name="test-workflow") as span:
        assert span == mock_span
        span.set_attribute.assert_any_call("workflow.id", 123)
        span.set_attribute.assert_any_call("workflow.name", "test-workflow")


@patch('app.services.observability_service.setup_observability')
@patch('app.services.observability_service.get_tracer')
def test_trace_agent_execution_context(mock_get_tracer, mock_setup):
    """Test agent execution tracing context manager."""
    mock_tracer = MagicMock()
    mock_span = MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    mock_get_tracer.return_value = mock_tracer
    
    service = ObservabilityService()
    
    with service.trace_agent_execution(
        agent_id=456,
        agent_name="test-agent",
        executor_id="executor_1"
    ) as span:
        assert span == mock_span
        span.set_attribute.assert_any_call("agent.id", 456)
        span.set_attribute.assert_any_call("agent.name", "test-agent")
        span.set_attribute.assert_any_call("executor.id", "executor_1")


@patch('app.services.observability_service.setup_observability')
@patch('app.services.observability_service.get_tracer')
def test_trace_operation_context(mock_get_tracer, mock_setup):
    """Test generic operation tracing context manager."""
    mock_tracer = MagicMock()
    mock_span = MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    mock_get_tracer.return_value = mock_tracer
    
    service = ObservabilityService()
    
    attributes = {"custom_attr": "value"}
    
    with service.trace_operation("test-operation", attributes=attributes) as span:
        assert span == mock_span
        span.set_attribute.assert_called_with("custom_attr", "value")


@patch('app.services.observability_service.setup_observability')
def test_record_metric(mock_setup):
    """Test recording a metric."""
    service = ObservabilityService()
    service.initialize()
    
    # Should not raise an exception
    service.record_metric(
        metric_name="test.metric",
        value=42.0,
        attributes={"label": "test"}
    )


@patch('app.services.observability_service.setup_observability')
def test_get_observability_service_singleton(mock_setup):
    """Test that get_observability_service returns singleton."""
    # Clear any existing global instance
    import app.services.observability_service as obs_module
    obs_module._observability_service = None
    
    service1 = get_observability_service()
    service2 = get_observability_service()
    
    assert service1 is service2


@patch('app.services.observability_service.setup_observability')
def test_initialize_observability_function(mock_setup):
    """Test initialize_observability convenience function."""
    config = ObservabilityConfig(service_name="test")
    
    initialize_observability(config)
    
    mock_setup.assert_called_once()
    
    service = get_observability_service()
    assert service._initialized is True
    assert service.config.service_name == "test"


@patch('app.services.observability_service.setup_observability')
@patch('app.services.observability_service.get_tracer')
def test_trace_workflow_error_handling(mock_get_tracer, mock_setup):
    """Test workflow tracing handles errors correctly."""
    mock_tracer = MagicMock()
    mock_span = MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    mock_get_tracer.return_value = mock_tracer
    
    service = ObservabilityService()
    
    with pytest.raises(ValueError):
        with service.trace_workflow(123, "test") as span:
            raise ValueError("Test error")
    
    # Verify error was recorded
    mock_span.record_exception.assert_called_once()
    mock_span.set_status.assert_called()
