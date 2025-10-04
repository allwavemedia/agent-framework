"""Telemetry initialization module (Story S11).
Provides idempotent init_telemetry for future OpenTelemetry wiring.
Currently uses noop providers; future story will add real exporters.
"""
from __future__ import annotations
from typing import Optional
import threading

_init_lock = threading.Lock()
_initialized = False


def init_telemetry(service_name: str, otlp_endpoint: Optional[str] = None) -> None:
    """Initialize tracing & metrics providers.

    Safe to call multiple times; subsequent calls are no-ops.
    Parameters
    ----------
    service_name: Name of the logical service (for resource attributes later)
    otlp_endpoint: Optional OTLP collector endpoint; if None/noop exporter used
    """
    global _initialized
    if _initialized:
        return
    with _init_lock:
        if _initialized:
            return
        # Placeholder: real implementation to set tracer & meter providers
        # TODO(S11-FOLLOWUP): Configure OTLP exporters when endpoint available
        # For now we simply mark initialization.
        _initialized = True

__all__ = ["init_telemetry"]
