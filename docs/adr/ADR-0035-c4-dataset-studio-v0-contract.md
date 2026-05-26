# ADR-0035: C4 Dataset Studio v0 Contract

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S5
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c4-dataset-studio.md

## Context

C4 capability needed a real vertical slice in Battle Workspace instead of a placeholder.
Without a dedicated dataset contract, users cannot prepare evaluation cases in-product and cannot version inputs before optimizer runs.

## Decision

1. Introduce arena-scoped `dataset_studio` state in `optimizer.workspace.registry_store`.
2. Expose C4 API endpoints under `/api/arenas/{arena_id}/datasets/*`.
3. Support minimal but complete v0 lifecycle:
   - create/select dataset,
   - add one row,
   - replace rows (JSONL-like import path),
   - validate rows,
   - save version snapshot.
4. Mark capability `c4` as `enabled` in frontend contracts and provide React UI with real calls.

## Alternatives Considered

1. Keep C4 as stub until full evaluator/metric design is ready.
2. Reuse legacy dataset CLI only, without UI/API slice.
3. Store datasets outside workspace state in a separate service at this stage.

## Consequences

### Positive

1. Product loop becomes wider: C1-C4 now visible and testable in one workspace.
2. Dataset preparation is no longer external-only; user can inspect and version data in UI.
3. C4 API is stable enough to extend in V2.3.S6 (metrics/evaluators studio).

### Negative / Trade-offs

1. Store remains JSON-file based, so concurrency/scaling are intentionally limited in v0.
2. Validation is basic by design; advanced checks will come in next slices.

## Implementation Notes

1. New store methods: dataset state, row operations, validation, versioning.
2. New dev-server handlers and DTO builders for C4 endpoints.
3. Frontend C4 panel includes create/select/edit/import/validate/save-version.
4. Targeted test gate extended with C4 checks in unit/integration/e2e smoke paths.

## Verification

1. `npm run test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/unit/test_frontend_contracts.py -q`
3. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
4. `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py -q`

## Links

1. `Roadmap.md` (`V2.3.S5`)
2. `optimizer/workspace/registry_store.py`
3. `optimizer/frontend/dev_server.py`
4. `frontend/src/App.tsx`
5. `docs/wiki/releases/v2.3.s5.md`
