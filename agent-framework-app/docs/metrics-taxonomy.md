# Metrics Taxonomy (Initial)

## Latency Metrics
- generate_workflow_latency_ms (histogram)
- visual_to_code_latency_ms (histogram)
- code_to_visual_latency_ms (histogram)
- execution_startup_latency_ms (histogram)

## Throughput / Volume
- workflows_generated_total (counter)
- workflows_executed_total (counter)
- workflow_events_streamed_total (counter)
- sandbox_executions_total (counter)

## Resource / Reliability
- sandbox_timeouts_total (counter)
- sandbox_memory_limit_hits_total (counter)
- checkpoint_write_failures_total (counter)
- resume_operations_total (counter)

## Security / Validation
- rejected_generation_requests_total (counter) # policy or validation failures
- auth_failed_logins_total (counter) (Epic 2)

## Gauges
- active_websocket_connections (gauge)
- queued_execution_requests (gauge)

## Notes
- Prefix suggestion: `aiwf_` if global namespace risk.
- Consider percentiles via histogram buckets for latency metrics.
