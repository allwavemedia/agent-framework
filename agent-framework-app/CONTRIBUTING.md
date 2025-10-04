# Contributing Guide

## Branching Model
- `main`: Protected, always releasable.
- Feature branches: `feat/<area>-<short-desc>`
- Fix branches: `fix/<issue-id>-<short-desc>`
- Documentation: `docs/<topic>`

## Commit Convention (Conventional Commits)
`type(scope): short imperative description`
Types: feat, fix, docs, chore, test, refactor, perf, ci, build, security

## Pull Request Checklist
- [ ] Linked issue (if applicable)
- [ ] Tests added/updated
- [ ] Lint & type checks pass
- [ ] Updated docs / README sections if needed
- [ ] No secrets committed

## Code Style
- Python: Black + isort + flake8 (configure later) / Type hints required.
- TypeScript: ESLint (recommended rules) + Prettier.

## Testing Policy
Minimum before merge:
- Backend unit tests for new services
- Frontend component tests for UI logic
- Integration tests for new API endpoints

## Issue Labels
- `priority:p0/p1/p2`
- `area:frontend`, `area:backend`, `area:exec-engine`, `area:infra`
- `type:security`, `type:performance`

## Review Guidelines
- Prefer small, focused PRs
- Request changes for missing tests, unclear naming, dead code
- Approve when code is cohesive, documented, and tested.
