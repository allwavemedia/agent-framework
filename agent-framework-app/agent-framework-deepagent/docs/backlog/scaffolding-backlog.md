# Scaffolding & Foundations Backlog

> Source: PO Master Checklist gaps (2025-10-03) – Convert critical & high-risk readiness items into story-sized tickets. Each story should be refined before dev.

## Legend

Priority: P0 (Must before Epic 1 mid), P1 (Before Epic 2), P2 (Post-MVP)  
Est Effort: S (<2h), M (0.5–1 day), L (1–2 days)

---
## Story S1: Establish Monorepo Tooling Baseline

- Priority: P0  
- Effort: M  
- Description: Add root `package.json` with workspaces, frontend package stub, shared package stub, and backend dependency management placeholder.  
- Acceptance Criteria (Refined):
  1. Root `package.json` defines workspaces exactly: `apps/frontend`, `apps/backend`, `packages/shared`, `packages/ui` (backend workspace reserved even if only placeholders initially).
  2. Root scripts present and runnable without error: `dev:frontend`, `dev:backend` (temporary echo or TODO placeholder), `build` (placeholder), `lint` (placeholder) – all exit zero.
  3. Frontend package: Vite React TS scaffold plus `tsconfig.json` extending root `tsconfig.base.json` with strict compiler options.
  4. Shared package: `src/types.ts` exports at least one sample type; package configured with proper name and `type: module`.
  5. UI package initialized (README + index barrel) to reserve namespace for future component system.
  6. Clean install (`npm install` or chosen PM) completes with zero errors/warnings causing non‑zero exit; lockfile committed.
  7. README Monorepo section updated with tree snippet including backend & packages and examples of root scripts usage.
  8. `.gitignore` (or equivalent) excludes `node_modules`, build outputs, coverage; no stray build artifacts committed.

## Story S2: Backend FastAPI Skeleton

- Priority: P0  
- Effort: M  
- Description: Create `apps/backend/app` with `main.py`, health route, placeholder router modules.
- Acceptance Criteria (Refined):
  1. Directory skeleton under `apps/backend/app/`: `api/routes`, `core`, `models`, `services`, `schemas` (empty placeholders permitted besides health).
  2. `main.py` exposes FastAPI `app`; `uvicorn app.main:app --reload` (run from `apps/backend`) starts without errors.
  3. Health endpoint in `api/routes/health.py` returns JSON: `{ status: "ok", service: "backend", timestamp: <ISO8601> }`.
  4. Minimal Pydantic settings module (e.g., `core/settings.py`) loads `APP_ENV` with default `development` without throwing if unset.
  5. README updated: backend run instructions, directory tree snippet, sample curl of `/health`.
  6. No business logic / DB code introduced yet (explicitly deferred) and this constraint noted in code comment or README.

## Story S3: Docker & Compose Bootstrap

- Priority: P0  
- Effort: M  
- Description: Provide `docker-compose.yml` for Postgres + backend + (future) execution-engine stub.
- Acceptance Criteria (Refined):
  1. Compose file defines services: `backend` (build from `apps/backend`) & `postgres` (pinned tag, e.g., `postgres:16-alpine`) with named volume `postgres_data`.
  2. Postgres service includes a healthcheck using `pg_isready` (interval ≤30s, retries ≥3); backend `depends_on` uses health condition.
  3. Dedicated network `aiwf_net` present; both services attached.
  4. After `docker compose up`, `curl http://localhost:8000/health` returns S2 JSON; port mapping documented.
  5. `.dockerignore` excludes build artifacts, caches, node_modules, virtualenvs; image build does not vendor unnecessary files.
  6. README updated: start (`docker compose up -d`), logs tail, teardown, and note on env var usage (placeholder okay).
  7. Restarting stack preserves Postgres data (document volume persistence verification step).

## Story S4: Environment & Secrets Baseline

- Priority: P0  
- Effort: S  
- Description: Expand `.env.example` with validation script & add doc on secret rotation plan.
- Acceptance Criteria (Refined):
  1. `.env.example` lists required keys: `APP_ENV`, `POSTGRES_URL`, `LLM_PROVIDER`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `JWT_SECRET`, `SANDBOX_CPU_LIMIT`, `SANDBOX_MEM_LIMIT` with inline comments; optional keys enumerated.
  2. Validation script (`scripts/validate_env.py` or `.ts`) exits non‑zero enumerating all missing keys; zero exit when complete.
  3. README gains “Environment Validation” section with example commands (local + CI) & guidance copying `.env.example` to `.env.local`.
  4. `.gitignore` ensures `.env.local` (& any non-example env files) are ignored.
  5. Secret rotation procedure documented (threat model extension or new `docs/security-operations.md`) describing cadence & storage (no plaintext secrets in repo).
  6. README (or doc) shows sample validator failure output snippet for missing keys.

## Story S5: Testing Framework Bootstrap

- Priority: P0  
- Effort: M  
- Description: Configure pytest backend, Vitest frontend, Playwright scaffold.
- Acceptance Criteria (Refined):
  1. Backend sample test (`apps/backend/tests/test_health.py`) using HTTPX/TestClient asserts `/health` status 200 & JSON schema from S2.
  2. Frontend sample test (`apps/frontend/src/__tests__/App.test.tsx`) using Vitest + React Testing Library passes via `npm test`.
  3. Playwright scaffold: config + `e2e/placeholder.spec.ts` (skipped) referencing a future flow; `npx playwright install` documented.
  4. CI workflow updated: test steps (backend & frontend) fail pipeline on errors (no `|| true`).
  5. README Testing section documents backend, frontend, e2e commands & philosophy (fast unit focus first).
  6. Sample tests have no external DB/network dependency (purely fast) and note this constraint for future additions.

## Story S6: CI Quality Gates Upgrade

- Priority: P1  
- Effort: S  
- Description: Enforce lint, type-check, and fail fast policies.
- Acceptance Criteria (Refined):
  1. ESLint + Prettier configs added at repo root (ESLint extends recommended + typescript plugin). Running `npm run lint` (placeholder added in S1) exits non‑zero on violations in `apps/frontend`, `packages/shared`.
  2. Backend type checking enabled via `pyproject.toml` (mypy) or `pyrightconfig.json`; command added to CI and local docs.
  3. CI workflow split into jobs: `lint`, `type-check`, `test` (parallel) with dependency fan‑in to an optional `build` job; any failure halts pipeline.
  4. Test job runs both backend `pytest` and frontend `npm test` with separate steps (ensures granular failure visibility).
  5. Code coverage placeholder step (commented) documented for future integration (no failing threshold yet).
  6. README gains a “CI & Quality Gates” subsection describing each job and how to run locally.
  7. Badge (build/test status) added to README referencing main branch.

## Story S7: Performance Harness Foundation

- Priority: P1  
- Effort: M  
- Description: Implement preliminary scripts to measure FR5/FR7 latency.
- Acceptance Criteria (Refined):
  1. `scripts/perf/` directory added with two scripts: `graph_add_nodes.(py|ts)` and `code_edit_latency.(py|ts)` producing JSON to stdout.
  2. Both scripts accept `--iterations` (default 10) & `--warmup` (default 1) flags; runtime errors exit non‑zero.
  3. Output schema documented in README and conforms to: `{ "metric": "<name>", "iterations": <n>, "p50_ms": <number>, "p95_ms": <number>, "p99_ms": <number>, "mean_ms": <number>, "stddev_ms": <number>, "timestamp": "ISO8601" }`.
  4. A performance harness README subsection explains how to run scripts locally and capture baseline artifact (saved under `perf-results/` ignored by VCS).
  5. CI not yet runs performance scripts (explicitly deferred) but a TODO comment references future gating story.
  6. Scripts are deterministic for sample workload (use seeded RNG or fixed data) to reduce variance; note limitations.

## Story S8: API Error Contract & Client Adapter

- Priority: P1  
- Effort: S  
- Description: Define uniform error JSON format & lightweight TS client.
- Acceptance Criteria (Refined):
  1. `docs/api-error-contract.md` created specifying JSON envelope: `{ error: { code: string, message: string, details?: object } }` plus HTTP ↔ code mapping table and version note.
  2. FastAPI exception handler (catching `HTTPException` + generic fallback) returns the contract; unhandled exceptions produce a `INTERNAL_ERROR` code without stack trace leak.
  3. Error response includes a stable `code` taxonomy (min: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `INTERNAL_ERROR`).
  4. Frontend client utility (in `packages/shared` or `packages/ui`) normalizes fetch/axios errors to a discriminated union type (documented in the contract file or local README section).
  5. Unit test (backend) asserts a forced validation error returns contract shape; frontend test asserts normalization produces expected union variant.
  6. README updated linking to contract doc.

## Story S9: State Management Decision & Implementation

- Priority: P1  
- Effort: M  
- Description: Choose Zustand or Redux Toolkit, document rationale, integrate store skeleton.
- Acceptance Criteria (Refined):
  1. Decision document (`docs/state-management-decision.md`) includes: options compared (Zustand vs Redux Toolkit), evaluation criteria (dev ergonomics, middleware ecosystem, performance, type safety), final choice with justification, and migration fallback note.
  2. Chosen store scaffold added under `apps/frontend/src/state/` with: root provider wiring, placeholder slices/modules for `workflow`, `editor`, `events` (each exports initial state + typed actions/selectors).
  3. Type-safe selector or hook pattern established (e.g., `useWorkflowState`) with JSDoc/TSDoc explaining usage.
  4. Minimal unit test(s) ensuring store initializes default state and one action mutates predictably.
  5. README updated removing TBD, adding a “State Management” subsection summarizing rationale and linking to decision doc.
  6. No cross-feature coupling introduced; slices remain independent with clearly scoped responsibilities documented in comments.

## Story S10: Security Threat Model Expansion

- Priority: P1  
- Effort: S  
- Description: Add STRIDE categorization & initial test mapping for T1–T6.
- Acceptance Criteria (Refined):
  1. Existing threat model table extended with columns: `STRIDE`, `Planned Test Type(s)`, `Status`.
  2. Each threat T1–T6 assigned a STRIDE category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege); multi-category threats list comma-separated.
  3. `Planned Test Type(s)` column lists at least one of: unit, integration, security, e2e; no row left blank.
  4. Add legend defining abbreviations & guidance how future test IDs will reference threats (e.g., `SEC-T1-001`).
  5. README (Security section) links to updated threat model and states expansion date.
  6. Any newly discovered threat while adding STRIDE (if found) either added as T7+ or documented as “Deferred” with rationale.

## Story S11: Metrics Instrumentation MVP

- Priority: P1  
- Effort: S  
- Description: Add OpenTelemetry instrumentation wrapper & a metrics exporter stub.
- Acceptance Criteria (Refined):
  1. Instrumentation module (e.g., `apps/backend/app/core/telemetry.py`) exposes `init_telemetry(service_name: str)` setting tracer + meter providers (noop exporter acceptable placeholder) and safe to call multiple times.
  2. One counter (e.g., `agent_framework_requests_total`) and one histogram (e.g., `agent_framework_request_duration_ms`) registered & used in health endpoint or trivial route.
  3. Configuration supports optional OTLP endpoint via env (`OTEL_EXPORTER_OTLP_ENDPOINT`); if unset, falls back gracefully without error.
  4. README Observability section updated with instructions: enabling telemetry, environment variables, and sample instrumentation snippet.
  5. Unit test (or lightweight test) asserts init does not raise with and without endpoint set (may mock provider); histogram/counter creation verified.
  6. Future TODO comment referencing metrics expansion (S11 follow-up) added to module.

## Story S12: Contribution & Onboarding Enhancements

- Priority: P2  
- Effort: S  
- Description: Add `docs/onboarding.md` with 15‑minute setup path & common pitfalls.
- Acceptance Criteria:
  1. Document published.
  2. Linked from README & CONTRIBUTING.

## Story S13: Sandbox Resource Policy Enforcement

- Priority: P2  
- Effort: M  
- Description: Enforce CPU/MEM/timeouts & unit tests for limit triggers.
- Acceptance Criteria:
  1. Limits configurable via env.
  2. Exceeding CPU/memory/time triggers structured event.

## Story S14: Local LLM Fallback Stub

- Priority: P2  
- Effort: S  
- Description: Deterministic stub for generation when no API key present.
- Acceptance Criteria:
  1. Module returns canned plan & code.
  2. Activated when key missing.

---
 
## Suggested Sequencing (Critical Path)

S1 → S2 → S3 → S4 → S5 → (Gate) → S6/S8/S9 parallel → S7 (after minimal front/back integration) → S10/S11 → Remaining P2 items.

## Open Decisions

- State management (S9) – schedule decision before UI scaffolding tasks expand.
- LLM provider configuration layering (single vs pluggable) – add if complexity increases.

## Risks

- Delaying S7 may push performance regressions late.
- Not enforcing CI failures early (S6) increases rework cost.

