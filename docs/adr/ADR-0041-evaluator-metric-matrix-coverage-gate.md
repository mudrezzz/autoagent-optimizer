# ADR-0041: Evaluator x Metric Matrix as Mandatory Coverage Gate

- Status: Accepted
- Date: 2026-05-28
- Slice: V2.4.S4
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c6-evaluators-matrix.md

## Context

After V2.4.S3 we had feature-aware metric availability, but evaluator assignment was still coarse:
evaluators were toggled globally and not explicitly bound to concrete metrics/signals.

This created ambiguity:

1. Enabled metric could exist without any evaluator actually responsible for scoring it.
2. Validation could pass evaluator count checks while semantic coverage was incomplete.
3. Users could not inspect/adjust evaluator responsibility in a deterministic way.

## Decision

Introduce explicit `Evaluator x Metric` matrix in C6 and enforce coverage in validation.

1. Add profile contract field `evaluator_metric_links`:
   - `evaluator_id`
   - `metric_kind` (`comparative` | `diagnostic`)
   - `metric_id`
   - `enabled`
2. Add API endpoint:
   - `POST /api/arenas/{arena_id}/evaluation/matrix/save`
3. Extend validation:
   - every enabled and available metric/signal must have at least one enabled evaluator link.
   - missing coverage raises `evaluator_metric_coverage_gap` (error).
4. Surface matrix in C6 UI with per-cell checkbox controls and explicit `Save matrix`.

## Alternatives Considered

1. Keep global evaluator toggles only (no matrix).
2. Infer evaluator coverage automatically from evaluator type and metric kind.
3. Store matrix in frontend only and derive backend state on validate.

## Consequences

### Positive

1. Coverage becomes explicit and auditable.
2. Validation catches semantic setup gaps before optimizer launch.
3. Evaluator assignment is now reproducible and versionable as part of evaluation profile.

### Negative / Trade-offs

1. Added configuration complexity in C6.
2. Added backend contract surface (`evaluator_metric_links` + new save endpoint).
3. Requires additional UI and test maintenance.

## Implementation Notes

1. `optimizer/workspace/registry_store.py`:
   - normalize/store `evaluator_metric_links`,
   - sync links with current metrics/evaluators,
   - add `save_arena_evaluation_evaluator_metric_links(...)`,
   - enforce validation error `evaluator_metric_coverage_gap`.
2. `optimizer/frontend/dev_server.py`:
   - include matrix in evaluation state payload,
   - add `/evaluation/matrix/save` handler.
3. `frontend/src/App.tsx` + `frontend/src/api.ts` + `frontend/src/types.ts`:
   - matrix rendering and editing,
   - `Save matrix` call,
   - state synchronization after all evaluation actions.

## Verification

1. `python -m pytest tests/unit/test_workspace_registry_store.py -q`
2. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
3. `npm --prefix frontend run test -- src/__tests__/app.workspace.test.tsx`
4. `npm --prefix frontend run build`

## Links

1. Roadmap slice: `V2.4.S4`
2. Wiki release note: `docs/wiki/releases/v2.4.s4.md`
