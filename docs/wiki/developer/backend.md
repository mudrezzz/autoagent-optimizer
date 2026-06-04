# Backend Guide

## C2 Endpoint

`POST /api/arenas/{arena_id}/candidates/select-for-tests`

Body:

```json
{
  "candidate_ids": ["cand_pattern_cleaner_v0"],
  "max_compile_attempts": 3
}
```

Response includes:

1. `candidate_set_draft` with updated `selected_for_tests` and `compile_readiness`.
2. `compile_gate` aggregate for selected candidates.

## Behavior Contract

1. Empty candidate selection -> validation error.
2. Unknown `candidate_id` -> validation error.
3. Internal retry/auto-fix before surfacing a user-visible issue.

## Tests

1. `tests/unit/test_c2_candidate_assembly.py`
2. `tests/integration/test_frontend_dev_server.py`

## C4 Endpoints

`GET /api/arenas/{arena_id}/datasets/state`

`POST /api/arenas/{arena_id}/datasets/create`

```json
{
  "name": "linkedin-stylizer-v1",
  "description": "Manual draft cases"
}
```

`POST /api/arenas/{arena_id}/datasets/select`

```json
{
  "dataset_id": "dset_1234567890"
}
```

`POST /api/arenas/{arena_id}/datasets/assign`

```json
{
  "dataset_ids": ["dset_1234567890", "dset_abcdefghij"]
}
```

`POST /api/arenas/{arena_id}/datasets/{dataset_id}/rows/add`

```json
{
  "row": {
    "case_id": "case_01",
    "input": "source text",
    "target_stage": "final",
    "expected_payload": {
      "answer": "target style text"
    },
    "expected": "target style text",
    "notes": "optional"
  }
}
```

`POST /api/arenas/{arena_id}/datasets/{dataset_id}/rows/replace`

```json
{
  "rows": [
    {
      "case_id": "case_01",
      "input": "source text",
      "target_stage": "retrieval",
      "expected_payload": {
        "evidence_ids": ["doc_12", "doc_53"]
      },
      "notes": ""
    }
  ]
}
```

`POST /api/arenas/{arena_id}/datasets/{dataset_id}/validate`

`POST /api/arenas/{arena_id}/datasets/{dataset_id}/save-version`

```json
{
  "label": "pre-run-baseline",
  "source": "manual"
}
```

Validation contract v2:

1. Error for an empty dataset.
2. Error for missing `case_id` or `input`.
3. Error for duplicate `case_id`.
4. Error for unknown `target_stage`.
5. Error for non-object `expected_payload`.
6. Warning for stage-specific missing expected values:
- retrieval: missing `expected_payload.evidence_ids`,
- rerank: missing `expected_payload.ranked_ids`,
- synthesis: missing `expected_payload.must_include`,
- final: missing `expected_payload.answer`.

## C4 Evaluation Endpoints

`GET /api/arenas/{arena_id}/evaluation/state`

`POST /api/arenas/{arena_id}/evaluation/metrics/suggest`

Response:

```json
{
  "status": "success",
  "action": "suggest_metric_proposal",
  "evaluation": {
    "latest_metric_proposal": {
      "proposal_id": "mp_1234567890",
      "status": "draft",
      "items": []
    }
  }
}
```

`POST /api/arenas/{arena_id}/evaluation/metrics/proposals/{proposal_id}/apply`

Body:

```json
{
  "proposal_item_ids": ["mpi_1234567890", "mpi_abcdefghij"]
}
```

`POST /api/arenas/{arena_id}/evaluation/metrics/save`

`POST /api/arenas/{arena_id}/evaluation/evaluators/save`

`POST /api/arenas/{arena_id}/evaluation/matrix/save`

`POST /api/arenas/{arena_id}/evaluation/stage-bindings/suggest`

`POST /api/arenas/{arena_id}/evaluation/stage-bindings/save`

`POST /api/arenas/{arena_id}/evaluation/stage-mapping/auto-map`

`POST /api/arenas/{arena_id}/evaluation/stage-mapping/save`

```json
{
  "stage_bindings": [
    {
      "binding_id": "sbind_123",
      "stage_ref": "retrieval.main",
      "target_stage": "retrieval",
      "match_policy": "primary_only",
      "enabled": true,
      "notes": "optional"
    }
  ]
}
```

`POST /api/arenas/{arena_id}/evaluation/budget/save`

`POST /api/arenas/{arena_id}/evaluation/validate`

`POST /api/arenas/{arena_id}/evaluation/save-version`

Feature-aware behavior:

1. Response includes `candidate_features` inferred from selected candidates (`mini_graph`).
2. Each comparative metric / diagnostic signal may include:
- `required_features`,
- `availability_status` (`available` / `unavailable`),
- `availability_reason`.
3. Unavailable metrics/signals are auto-disabled on backend before validation.
4. Response includes `evaluator_metric_links` matrix (`evaluator_id`, `metric_kind`, `metric_id`, `enabled`, `compatibility_status`, `compatibility_reason`).

Metric-crafting behavior:

1. `suggest` creates a draft proposal and does not mutate comparative metrics or diagnostic signals.
2. proposal items can be comparative metrics or diagnostic signals.
3. `apply` accepts explicit `proposal_item_ids` and applies only those items.
4. `apply` marks the proposal as `applied`, creates an evaluation profile version with source `metric_crafting_apply`, and refreshes evaluator x metric compatibility links.
5. unsupported evaluator links for newly applied metrics are normalized to `enabled=false`.

Evaluator coverage behavior:

1. `evaluator_metric_links` stores explicit mapping for comparative and diagnostic targets.
2. `optimizer.evaluation.evaluator_adapters` is the source of truth for adapter metadata.
3. `GET /api/evaluation/evaluator-adapters` returns the adapter catalog.
4. Evaluation state enriches each evaluator with:
- `adapter_kind`,
- `requires_dataset`,
- `requires_llm`,
- `requires_stage_mapping`,
- `supported_metric_refs`,
- `budget_cost_model`,
- `adapter_status`,
- `adapter_status_reason`.
5. Validation returns `evaluator_metric_coverage_gap` when enabled metric/signal has no enabled compatible evaluator link.
6. Normalization forces unsupported evaluator x metric pairs to `enabled=false`, even when API payload sends `enabled=true`.
7. Validation may still return `evaluator_metric_incompatible` for non-normalized in-memory data, but persisted API state should not reach that condition.
8. Validation returns `evaluator_requires_dataset` / `evaluator_requires_llm` when enabled evaluators miss required resources/config.

Stage binding behavior:

1. `suggest` endpoint returns rule-based proposals and coverage without mutating profile state.
2. `save` endpoint persists normalized bindings and recomputes `stage_binding_coverage`.
3. Validation checks enabled non-final diagnostics against required `target_stage` bindings.
4. Validation may return:
- `stage_ref_missing`,
- `stage_ref_unresolved`,
- `stage_ref_ambiguous`,
- `stage_ref_multi_match`,
- `stage_ref_policy_violation`.

Stage mapping behavior (`target_stage-first`):

1. Auto-map endpoint builds per-candidate mappings from required diagnostic stages.
2. Save endpoint persists manual overrides (`selected_node_ids`, `enabled`, `notes`).
3. Save endpoint treats a single selected node with `source=manual` or manual confirmation notes as `bound` with `confidence >= 0.80`.
4. Validation deduplicates repeated stage/candidate mapping issues when several diagnostics require the same stage.
5. Validation is driven by mapping coverage and may return:
- `stage_mapping_missing`,
- `stage_mapping_unresolved`,
- `stage_mapping_ambiguous`,
- `stage_mapping_policy_violation`.
6. Legacy `stage_bindings` API remains available as compatibility wrapper.

Validate report statuses:

1. `ready` - no issues.
2. `warnings` - warning issues only.
3. `invalid` - at least one error issue.

## C5 Optimizer Endpoints

`GET /api/arenas/{arena_id}/optimizer/state`

`POST /api/arenas/{arena_id}/optimizer/save`

```json
{
  "methods": [
    { "method_id": "random_search", "title": "Random search", "description": "baseline", "enabled": true }
  ],
  "controls": [
    { "control_id": "tune_prompts", "title": "Tune prompts", "description": "scope", "enabled": true }
  ],
  "run_plan": {
    "epochs_total": 3,
    "candidates_per_epoch": 4,
    "max_parallel_trials": 2,
    "early_stop_patience": 1
  },
  "budget": {
    "max_cases": 24,
    "max_llm_calls": 200,
    "max_cost_usd": 8.0,
    "max_runtime_minutes": 30
  }
}
```

`POST /api/arenas/{arena_id}/optimizer/validate`

`POST /api/arenas/{arena_id}/optimizer/save-version`

`POST /api/arenas/{arena_id}/optimizer/launch`

Launch guardrails verify:

1. C2 selected candidates and compile gate.
2. C4 assigned datasets.
3. C4 evaluation profile status.
4. Valid C5 run plan, budget, and methods.
