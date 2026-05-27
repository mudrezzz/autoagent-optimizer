# C4 Dataset Studio

C4 is used to prepare test datasets before optimization.

## Available in v0

1. Create a dataset inside Battle Workspace.
2. Mark datasets via checkboxes and save arena assignment with `Save`.
3. Open `Details` to preview first 5 rows.
4. Open `Edit` to enter dedicated dataset editor screen.
5. In editor: add/delete/edit rows and import JSONL.
6. Validate dataset (`Validate`) and save snapshot (`Save version`).
7. Open `Metrics` tab and configure evaluation profile:
- comparative metrics,
- diagnostic signals,
- evaluators,
- budget limits.
8. Run `Validate profile` and save profile version with `Save version`.

## Screenshots (Real UI)

### Dataset Tab

![C4 Dataset Tab](../assets/screenshots/real-workspace-c4-datasets.png)

### Metrics Tab

![C4 Metrics Tab](../assets/screenshots/real-workspace-c4-metrics.png)

## Minimal Flow

1. Open capability `C4 Dataset Studio`.
2. Enter dataset name and click `Create dataset`.
3. Select dataset in list and click `Save`.
4. Click `Edit` on the target dataset.
5. Update rows, then click `Save changes`.
6. Click `Validate`.
7. If there are no errors, click `Save version`.
8. Switch to `Metrics`, configure metrics/evaluators/budget, and save each block.
9. Click `Validate profile`, then `Save version` for evaluation profile.

## Case Row Format

Each row contains:

1. `case_id` - unique case identifier.
2. `input` - source text/query.
3. `expected` - expected output/behavior.
4. `notes` - optional comment.

## How to Read Validate Results

1. `error` - blocking issue (for example: empty `input`, duplicate `case_id`, empty dataset).
2. `warning` - non-blocking issue (for example: empty `expected`).

## Next Step

After saving dataset version, proceed to the next capability slice (Optimizer Setup in C5).
