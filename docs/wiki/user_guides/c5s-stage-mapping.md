# C5s Stage Mapping

## Purpose

Use `Stage Mapping` to bind non-final diagnostic stages (`retrieval`, `rerank`, `synthesis`) to candidate runtime nodes.

This step is required only when such diagnostics are enabled in `Metrics`.

## How to Use

1. Open a battle workspace.
2. Go to `Stage Mapping` in the left wizard menu.
3. Wait for auto-init:
- if suggestions exist, rows appear automatically;
- if no suggestions exist, continue in manual mode.
4. Add or edit rows manually:
- `Add row` to create a new mapping line,
- choose `target_stage`,
- choose candidate,
- provide `node ids`,
- optionally write notes.
5. Use `Refresh auto-map` when candidate set changed and you want new suggestions.
6. Click `Save mapping`.
7. Click `Validate profile` to confirm mapping coverage.

## Result

If required stage coverage is valid, `Evaluators` step becomes available in wizard flow.
