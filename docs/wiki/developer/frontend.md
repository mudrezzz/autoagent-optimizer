# Frontend Guide

## C2 UI Contract

In the candidate list:

1. Candidate checkbox for test selection.
2. `Select for tests` button to trigger internal preparation.
3. Candidate details via accordion.

## C3 UI Contract

In pattern library:

1. One `selected` checkbox per pattern row.
2. `Save` button persists the current selected pattern set.
3. Before `Save`, changes stay local (`dirty` state).
4. Pattern details are available via accordion and do not affect selection.

## UX Principles

1. Validation/compile steps are hidden as internal technical operations.
2. User interacts only with business actions (selecting candidates for tests).
3. Selection pattern is unified between C2/C3: single checkbox + explicit save action.
4. Errors are shown only after auto-fix/retry has failed.

## Tests

1. `frontend/src/__tests__/app.workspace.test.tsx`

## C4 UI Contract

In C4 Dataset Studio:

1. The screen has two modes: `list` and `edit`.
2. In `list` mode, datasets are shown as candidate-like rows with checkboxes.
3. `Save` stores selected dataset assignment to arena.
4. `Details` expands a preview of first 5 rows.
5. `Edit` opens a dedicated editor screen with breadcrumbs.
6. In `edit` mode: add/delete/edit rows, JSONL import, `Save changes`, `Validate`, `Save version`.
7. Row editor supports stage-aware fields:
- `target_stage` selector (`retrieval | rerank | synthesis | final`),
- `expected` text input (auto-mapped into `expected_payload` per stage).

In C4 Metrics & Evaluators Studio:

1. Comparative metrics are edited via checkboxes + weights and saved with `Save metrics`.
2. Diagnostic signals are edited via checkboxes and saved with `Save diagnostics`.
3. Evaluators are edited via checkboxes and saved with `Save evaluators`.
4. Evaluator x Metric matrix is edited via per-cell checkboxes and saved with `Save matrix`.
5. `Stage bindings (stage_ref)` card allows manual edit plus auto-suggest (`Suggest stage refs`) and explicit persist (`Save stage bindings`).
6. Budget is edited via numeric fields and saved with `Save budget`.
7. `Validate profile` returns status + issues.
8. `Save version` snapshots the evaluation profile.
9. Unavailable metrics/signals (based on candidate features) are rendered as disabled controls with reason text.
10. Candidate feature summary is displayed at the top of C5 Metrics screen.

State is loaded through `fetchArenaDatasetState` + `fetchArenaEvaluationState` and refreshed after each C4 action.

## C5 UI Contract

In C5 Optimizer Setup:

1. `Methods` and `Optimization controls` are checkbox-based.
2. `Run plan` and `Budget limits` use numeric fields.
3. `Save setup` persists the profile in backend.
4. `Validate` runs preflight guardrails and returns status + issues.
5. `Launch` creates a queued run only when guardrails have no errors.
6. `Save profile version` snapshots optimizer setup.
7. `Launch queue` shows recent run records.

C5 state is loaded via `fetchArenaOptimizerState` and refreshed after each C5 action.
