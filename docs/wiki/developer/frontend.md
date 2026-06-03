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

Evaluation steps (`C5/C5s/C6`) use a split contract:

1. C5 (`Metrics`) edits comparative metrics + diagnostic signals + weights.
2. C5s (`Stage Mapping`) handles auto-map, manual rows, and mapping coverage.
3. C6 (`Evaluators`) edits evaluator list + matrix links only.
4. `Validate profile` and `Save version` are executed from C6.
5. Unavailable metrics/signals (based on selected candidates) stay disabled with reason text.
6. Candidate feature summary is shown at the top of C5.

State is loaded through `fetchArenaDatasetState` + `fetchArenaEvaluationState` and refreshed after each C4 action.

## C5 / C5s / C6 Evaluation Contract

1. C5 (`Metrics`) owns only comparative + diagnostic metric setup.
2. C5s (`Stage Mapping`) is a dedicated wizard step between C5 and C6.
3. C6 (`Evaluators`) owns evaluator list + evaluator x metric matrix.
4. Budget controls are not shown in C6; budget lives in C7.
5. If non-final diagnostics are enabled (`retrieval/rerank/synthesis`), C5s coverage must be ready before C6 is unlocked.

## Contextual Chat Contract (V2.4.S6)

1. Frontend always posts to `postArenaChatMessage` with:
2. `capabilityId` from active wizard step,
3. optional `contextAction` for `Run action`.
4. Supported contextual chat capabilities: `c2`, `c4`, `c5`, `c5s`, `c6`, `c7`.
5. Backend returns `copilot_context` (`resolved_action`, `allowed_actions`, `summary`).
6. For non-C2 actions frontend performs targeted refresh:
7. C4 -> `loadC4DatasetState`,
8. C5/C5s/C6 -> `loadC4EvaluationState`,
9. C7 -> `loadC5OptimizerState`.

## Debug Drawer Contract (V2.4.S7)

1. Raw `jsonText` must not be rendered inside capability content panels.
2. Workspace topbar exposes `Debug`.
3. `Debug` opens `debug-drawer` with latest `jsonText` plus compact metadata.
4. `Export snapshot` remains a download action for `lastPayload`.
5. Future debug/timeline additions should extend the drawer/devtools surface, not the main wizard panels.

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
