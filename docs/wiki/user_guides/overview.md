# User Guide Overview

## Real UI Screenshots

### Battles Hub

![Battles Hub](../assets/screenshots/real-battles-hub.png)

### Battle Workspace (C2)

![Battle Workspace C2](../assets/screenshots/real-workspace-c2.png)

### Battle Workspace (C3)

![Battle Workspace C3](../assets/screenshots/real-workspace-c3.png)

### Battle Workspace (C6 Evaluators)

![Battle Workspace C6](../assets/screenshots/real-workspace-c6-evaluators-matrix.png)

## Core User Flow

1. Create or open a battle in Battles Hub.
2. In Battle Workspace, describe the task in chat.
3. Review generated architecture candidates.
4. If needed, select patterns in C3 and save via `Save`.
5. Prepare test cases in C4 Dataset Studio, mark required datasets, and save assignment to arena.
6. In C4/C6, configure metrics, evaluators, and evaluator-metric matrix, then run `Validate profile`.
7. In C2, select candidates for tests (checkboxes) and run `Select for tests`.
8. In C5, save optimizer setup, run `Validate` (preflight guardrails), then click `Launch`.
9. Monitor launch queue and proceed to run-monitor stages.

## Internal Processes (Hidden from User)

1. Candidate validation and compile readiness checks.
2. Internal auto-fix/retry attempts for preparation errors.

The user should see only the final state: candidate ready for tests, or explicit request for manual attention.
