# C5 Optimizer Setup

## What It Is

C5 is the stage before optimization launch.
Here you save launch profile and validate preflight guardrails.

## What You Configure

1. `Methods` - configuration search strategies (`random/grid/optuna`, etc.).
2. `Optimization controls` - which architecture parts are allowed to change.
3. `Run plan` - epochs, candidates per epoch, parallelism, early stop.
4. `Budget limits` - limits for cases, LLM calls, cost, and runtime.

## Screenshot (Real UI)

![C5 Optimizer Setup](../assets/screenshots/real-workspace-c5.png)

## Main Flow

1. Open capability `C5 Optimizer Run Monitor`.
2. Select required methods and controls.
3. Fill `Run plan` and `Budget limits`.
4. Click `Save setup`.
5. Click `Validate` and review preflight status.
6. If status is `ready` or `warnings`, click `Launch`.
7. Optionally click `Save profile version`.

## Guardrails (Launch Blockers)

1. No candidates selected for tests in C2.
2. Candidate compile gate is not `ready`.
3. No datasets assigned in C4.
4. C4 evaluation profile has `invalid` status.
5. Invalid run-plan/budget fields (for example: `epochs_total = 0`).

## What You See After Launch

1. `Launch queue` gets a new `run_id` with `queued` status.
2. `Debug` drawer shows payload of the latest launch action when needed.

The next C5 slice extends this into a detailed Run Monitor timeline.
