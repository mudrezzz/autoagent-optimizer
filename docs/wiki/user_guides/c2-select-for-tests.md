# C2 Candidate Selection for Tests

## What Changed (V2.3.S4)

C2 no longer has a manual `Assemble + Compile` step.

New UX:

1. Select candidates via checkboxes.
2. Click `Select for tests`.
3. System runs internal preparation automatically.

## Real C2 Screen

![C2 Candidate Selection](../assets/screenshots/real-workspace-c2.png)

## What Happens Internally

1. Validates selected set.
2. Compiles selected candidates only.
3. Runs multiple auto-retry attempts.
4. Attempts auto-fix for known `dsl_stub_ref` issues.
5. Shows user-facing issue only when preparation cannot be recovered.

## How to Confirm Success

1. Candidate is marked as selected.
2. Candidate set reaches `ready` status.
3. Chat shows system message about preparation result.

## When an Issue Appears

Issue is shown only after internal preparation retries are exhausted.
