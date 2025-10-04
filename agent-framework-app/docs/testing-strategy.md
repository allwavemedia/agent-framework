# Testing Strategy

## Overview
Adopt a pyramidal test strategy to ensure fast feedback and reliability.

## Framework Choices (Proposed)
| Layer | Backend | Frontend | Notes |
|-------|---------|----------|-------|
| Unit  | pytest  | Vitest + React Testing Library | Aim for >70% critical logic coverage early |
| Integration | pytest (with testcontainers or docker-compose) | API contract tests via MSW | DB + API interaction |
| E2E   | Playwright | Playwright | Critical user journeys (generate, edit visually, run, save) |
| Performance | Locust / custom harness | Scripted browser automation | Latency budgets FR5/FR7 |

## Coverage Targets (MVP)
- Backend: 70% statements, 80% for core orchestration module
- Frontend: 60% overall, 80% for synchronization logic module
- Raise thresholds post-MVP by +10–15%

## Naming & Structure
```
/apps/backend/app/tests/unit/
/apps/backend/app/tests/integration/
/apps/backend/app/tests/perf/
/apps/frontend/src/__tests__/
```

## Performance Test Harness Outline
- Script to simulate 10 sequential node additions (visual→code) measuring median & p95
- Script to apply synthetic code edits and measure code→visual latency
- Export metrics as JSON for CI gating in future

## Test Data Strategy
- Factories (e.g., factory_boy or simple helpers) for Users, Workflows
- Deterministic seeds for workflow graphs

## Mocking & Isolation
- Use dependency injection for LLM client allowing a fake implementation returning canned plan
- Use MSW on frontend for API stubbing during component tests

## CI Execution Order
1. Lint & type checks
2. Backend unit
3. Frontend unit
4. Integration (parallel containers)
5. E2E (smoke subset on PR; full suite nightly)

## Exit Criteria for Story Acceptance
- All new logic has unit tests
- Any new endpoint has at least one integration test
- Critical path user journey unaffected (smoke E2E pass)

## Future Enhancements
- Mutation testing for critical modules
- Contract testing (OpenAPI schema drift detection)
- Automated performance regression budget enforcement
