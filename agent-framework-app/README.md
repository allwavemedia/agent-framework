# AI Workflow Builder

An interactive application that converts natural language prompts into executable Python workflow code using the Microsoft Agent Framework, providing a synchronized visual graph and code editor with secure sandboxed execution and real-time event streaming.

## Key Features (MVP)
- Natural language → workflow code (FR1)
- Visual graph rendering & editing (FR2–FR5)
- Code editor with reverse sync (FR6–FR7)
- Secure execution sandbox + event streaming (FR8–FR9)
- (Post-Epic 1+) Auth & workflow persistence (FR11–FR12)

## Repository Structure (Planned)
```
/ai-workflow-builder
  /apps
    /frontend
    /backend
  /packages
    /shared
    /ui
  /execution-engine
```

## Tech Stack
| Layer | Choice | Notes |
|-------|--------|-------|
| Backend | Python 3.11 + FastAPI | Async, WebSockets, Pydantic |
| AI Core | Microsoft Agent Framework | Core workflow generation & execution |
| Frontend | React + TypeScript + Vite | Split-pane UI, fast HMR |
| State Mgmt | TBD (Zustand vs Redux Toolkit) | Decide before Story 1.4 |
| DB | PostgreSQL | Persistence & checkpoints metadata |
| Sandbox | Docker | Resource & security isolation |
| Observability | OpenTelemetry | Traces: workflow.run / executor.process |

## Getting Started
1. Clone repo
2. Copy `.env.example` to `.env` and fill secrets
3. Start infrastructure (placeholder: `docker compose up -d` once added)
4. Backend: `cd apps/backend && uvicorn app.main:app --reload`
5. Frontend: `cd apps/frontend && npm run dev`

## Environment Variables
See `.env.example` for all required keys.

## Testing (Initial Policy)
- Unit: backend (pytest), frontend (Vitest) – frameworks to be finalized
- Integration: API + DB using test containers
- E2E: Playwright (generate → run workflow smoke)

## CI/CD
GitHub Actions workflow `ci.yml` runs backend & frontend unit tests (placeholder) and sets up Postgres.

## Security & Risks
See `docs/security-threat-model.md`.

## Metrics
Initial taxonomy in `docs/metrics-taxonomy.md`.

## Performance

Baseline performance harness (Story S7) provides simple latency benchmarks for core operations. Two scripts live under `scripts/perf/`:

| Script | Metric Name | Description |
|--------|-------------|-------------|
| `graph_add_nodes.py` | `graph_add_nodes` | Simulates adding batches of nodes to an in-memory graph |
| `code_edit_latency.py` | `code_edit_diff` | Simulates computing a diff for iterative code edits |

### Running Locally

```bash
python scripts/perf/graph_add_nodes.py --iterations 15 --warmup 2
python scripts/perf/code_edit_latency.py --iterations 15 --warmup 2
```

Each script prints a JSON payload:

```json
{
  "metric": "graph_add_nodes",
  "iterations": 15,
  "p50_ms": 1.23,
  "p95_ms": 2.10,
  "p99_ms": 2.30,
  "mean_ms": 1.40,
  "stddev_ms": 0.20,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Capturing a Baseline

1. Run both scripts with default iterations (10) on a quiet machine.
2. Copy outputs into `perf-results/baseline-(date).json` (directory is gitignored).
3. Document anomalies (if any) in a lightweight CHANGELOG entry (future story).

> CI integration is intentionally deferred; a follow-up story will define thresholds and gating.

## Roadmap Reference
Epics in `docs/prd/5-epic-list.md` define sequencing.

## Contribution
See `CONTRIBUTING.md`.
