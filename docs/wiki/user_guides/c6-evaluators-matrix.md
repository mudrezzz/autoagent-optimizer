# C6 Evaluators Matrix

## Purpose

Use C6 to explicitly define which evaluator is responsible for which metric/signal.

This prevents invalid evaluation profiles where metrics are enabled but no evaluator actually scores them.

## Real UI Screenshot

![C6 Evaluators Matrix](../assets/screenshots/real-workspace-c6-evaluators-matrix.png)

## How to Use

1. Open a battle workspace.
2. Go to `Evaluators` in the left wizard menu.
3. Enable required evaluators in the `Evaluators` card.
4. In `Evaluator x Metric matrix`, check cells to assign evaluator coverage:
- rows are comparative metrics and diagnostic signals,
- columns are enabled/available evaluators.
5. Click `Save matrix`.
6. In `Stage mapping`, define non-final mapping from `target_stage` to candidate nodes:
- click `Auto-map stages` to generate mapping rows automatically,
- review per-candidate selected node ids and adjust manually if needed,
- click `Save mapping`.
7. Click `Validate profile`:
- `ready`: matrix and stage bindings are valid,
- `invalid`: missing evaluator links or invalid stage binding coverage.

## Validation Rule

 For each enabled metric/signal, at least one enabled evaluator must have an enabled matrix link.

For enabled non-final diagnostics, valid stage mapping rows must exist for required target stages and selected candidates.
