# State Management Decision (Story S9)

## Purpose

Document evaluation and selection of frontend global state approach.

## Options Considered

| Option | Pros | Cons | Notes |
|--------|------|------|-------|
| Zustand | Minimal API, good TS inference, flexible middleware | Less opinionated structure, ecosystem smaller than Redux Toolkit | Lean for early iteration |
| Redux Toolkit | Mature ecosystem, devtools, established patterns | Boilerplate overhead, can feel heavy for small app | Easier scaling if complexity spikes |

## Evaluation Criteria

| Criterion | Description | Weight (1-5) | Zustand Score | RTK Score |
|----------|-------------|-------------|---------------|-----------|
| Dev Ergonomics | Boilerplate & DX friction | 5 | 4 | 3 |
| Middleware Ecosystem | Plugins / tooling availability | 3 | 3 | 5 |
| Performance | Render minimization, selector efficiency | 4 | 4 | 4 |
| Type Safety | Depth of inference, action typing clarity | 4 | 4 | 4 |
| Learning Curve | Onboarding cost for new devs | 3 | 4 | 3 |

> Scores are preliminary; finalize after prototype spike.

## Decision (Provisional)

Adopt **Zustand** initially for rapid iteration; re-evaluate if:

- >3 complex cross-cutting concerns emerge
- Need for advanced middleware (complex persistence, sagas, etc.)

## Implementation Plan

1. Create `packages/shared/state/` with initial store slices (feature-focused).
2. Provide a `createStore()` factory consolidating slices for testability.
3. Co-locate slice tests verifying default state & basic actions.
4. Establish naming: `use<Feature>Store` hooks exporting selectors.
5. Cross-feature selectors reside in `selectors/` subdirectory.

## Slice Template (Example)

```ts
// packages/shared/state/user.slice.ts
import { create } from 'zustand';

interface UserState {
  id?: string;
  name?: string;
  setUser: (id: string, name: string) => void;
  clear: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  id: undefined,
  name: undefined,
  setUser: (id, name) => set({ id, name }),
  clear: () => set({ id: undefined, name: undefined })
}));
```

## Testing Guidelines

- Unit test each slice's initial state & action side-effects.
- Avoid coupling tests to internal implementation details.
- Add performance test later if selectors become complex.

## Re-evaluation Triggers

| Trigger | Action |
|---------|--------|
| Increased middleware needs | Assess RTK migration path |
| Complex undo/redo flows | Prototype RTK + devtools |
| Performance degradation | Audit selectors & consider RTK batching |

## Migration Considerations

If migrating to Redux Toolkit:

- Wrap Zustand access behind module exports now to reduce refactor surface.
- Provide action creator parity where possible.
- Plan an automated migration script to generate RTK slices.
