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
6. In `Stage bindings (stage_ref)`, define stage mappings for non-final diagnostics:
- click `Suggest stage refs` to auto-fill rule-based bindings,
- adjust `stage_ref`, `target_stage`, and `match_policy` if needed,
- click `Save stage bindings`.
7. Click `Validate profile`:
- `ready`: matrix and stage bindings are valid,
- `invalid`: missing evaluator links or invalid stage binding coverage.

## Validation Rule

 For each enabled metric/signal, at least one enabled evaluator must have an enabled matrix link.

For enabled non-final diagnostics, at least one valid stage binding must exist for the required target stage.
