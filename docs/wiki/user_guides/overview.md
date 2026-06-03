# User Guide Overview

## Real UI Screenshots

### Battles Hub

![Battles Hub](../assets/screenshots/real-battles-hub.png)

### Battle Workspace (C2)

![Battle Workspace C2](../assets/screenshots/real-workspace-c2.png)

### Battle Workspace (C3)

![Battle Workspace C3](../assets/screenshots/real-workspace-c3.png)

### Battle Workspace (C4 Dataset Editor v2)

![Battle Workspace C4 Dataset Editor](../assets/screenshots/real-workspace-c4-dataset-editor-v2.png)

### Battle Workspace (C5 Metrics)

![Battle Workspace C5 Metrics](../assets/screenshots/real-workspace-c5-metric-proposal.png)

### Battle Workspace (C6 Evaluators)

![Battle Workspace C6](../assets/screenshots/real-workspace-c6-evaluators-matrix.png)

### Battle Workspace Debug Drawer

![Battle Workspace Debug Drawer](../assets/screenshots/real-workspace-debug-drawer.png)

## Core User Flow

1. Create or open a battle in Battles Hub.
2. In C3, select architecture patterns and save via `Save`.
3. In C2, describe the task and click `Generate` to build candidate architectures.
4. In C2, select candidates via checkboxes and run `Select for tests`.
5. In C4, prepare datasets, assign selected datasets, and save.
6. In C5, configure comparative metrics + diagnostic signals, or use `Suggest metrics` to create a HITL proposal.
7. In C5s, verify stage mapping (auto-map + manual adjustments if needed).
8. In C6, configure evaluators and `Evaluator x Metric` matrix.
9. In C7, save optimizer setup, run `Validate`, then click `Launch`.
10. Monitor launch queue and proceed to run-monitor stages.

## Contextual Right Chat (V2.4.S6)

Right chat is step-aware and changes behavior by active wizard tab:

1. C2: regular task chat + candidate generation.
2. C4: contextual action `add_dataset_row`.
3. C5: contextual action `suggest_metrics`.
4. C5s: contextual actions `auto_map_stage_mappings` / `add_mapping_row`.
5. C6: contextual action `autofill_matrix_links`.
6. C7: contextual action `validate_optimizer_setup`.

## Debug Drawer (V2.4.S7)

The workspace topbar has a `Debug` button for technical inspection.

1. The main workspace does not show inline raw JSON blocks.
2. `Debug` opens a drawer with the latest runtime snapshot.
3. `Export snapshot` still downloads the latest payload.
4. The drawer is intended for debugging and support, not for the normal user flow.

## Internal Processes (Hidden from User)

1. Candidate validation and compile readiness checks.
2. Internal auto-fix/retry attempts for preparation errors.

The user should see only the final state: candidate ready for tests, or explicit request for manual attention.
