# Batch 2 Refinement Summary (Stories S7, S10, S11)

## Scope

This document captures the refinements applied to performance, security threat modeling, and observability/metrics stories plus supporting scaffolding artifacts.

## Stories Refined

| Story | Area | Key Enhancements |
|-------|------|------------------|
| S7 | Performance Harness | Added deterministic perf scripts, JSON schema, baseline capture process, README section |
| S10 | Security Threat Model | STRIDE categorization, planned test type column, legend, README linkage, new threats handling rule |
| S11 | Metrics Instrumentation | Telemetry module path, idempotent init, counter & histogram spec, env var fallback, test expectations |

## Artifacts Created

| Artifact | Path | Purpose |
|----------|------|---------|
| Base TS Config | `tsconfig.base.json` | Shared compiler options & path aliases |
| Docker Ignore | `.dockerignore` | Reduce build context size & exclude transient assets |
| Perf Script (Graph) | `scripts/perf/graph_add_nodes.py` | Measures synthetic graph node add latency |
| Perf Script (Diff) | `scripts/perf/code_edit_latency.py` | Measures synthetic code diff latency |
| Telemetry Stub | `apps/backend/app/core/telemetry.py` | Idempotent instrumentation initializer placeholder |
| Env Validator | `scripts/validate_env.py` | Ensures required env keys present (JSON output) |
| Error Contract Doc | `docs/api-error-contract.md` | Canonical error response schema + taxonomy |
| State Mgmt Decision | `docs/state-management-decision.md` | Comparative evaluation & provisional choice |
| Performance README Section | `README.md` | Usage guidance & baseline capture workflow |

## Acceptance Criteria Coverage Highlights

- Deterministic performance workloads via fixed RNG seeds.
- Output JSON schema enumerates p50, p95, p99, mean, stddev, timestamp.
- Telemetry initialization safe for multiple calls (idempotent guard + lock).
- Threat model expansion ready for STRIDE mapping & future test ID referencing.
- Metrics story scaffolded: placeholder module + counter/histogram design documented (implementation deferred until route wiring).

## Deferred / Follow-Up Items

| Item | Rationale | Linked Story (Future) |
|------|-----------|-----------------------|
| CI performance gating | Avoid premature flakiness before baseline stabilization | New story (post-S7) |
| Real OTLP exporters | Requires infra endpoint provisioning | Follow-up to S11 |
| Additional error domains | Needs broader feature surface | Rolling updates |
| Comprehensive state slice tests | Await actual feature slices | Post state implementation |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Synthetic perf not representative | Misleading early optimizations | Mark scripts as baseline only; evolve workload as features land |
| Telemetry stub forgotten | Missing early observability | TODO marker + story linkage in code |
| Threat model drift | Security gaps | Incorporate periodic review checkpoint in CI docs (future) |

## Next Batch Recommendations (S12–S14)

1. Implement minimal health endpoint wiring & integrate telemetry counter usage.
2. Begin wiring workflow graph domain model to replace synthetic perf placeholders.
3. Add initial integration test harness for API error contract validation.

## Summary

Batch 2 solidifies foundational non-functional scaffolding (performance measurement, security categorization, and observability hooks) reducing ambiguity and derisking subsequent functional implementation stories.
