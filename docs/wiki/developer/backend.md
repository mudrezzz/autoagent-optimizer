# Backend Guide

## C2 endpoint

`POST /api/arenas/{arena_id}/candidates/select-for-tests`

Body:

```json
{
  "candidate_ids": ["cand_pattern_cleaner_v0"],
  "max_compile_attempts": 3
}
```

Response включает:

1. `candidate_set_draft` с обновленными `selected_for_tests` и `compile_readiness`.
2. `compile_gate` агрегат по выбранным кандидатам.

## Контракт поведения

1. Пустой выбор кандидатов -> validation error.
2. Неизвестный `candidate_id` -> validation error.
3. Внутренние retry/auto-fix до пользовательского issue.

## Тесты

1. `tests/unit/test_c2_candidate_assembly.py`
2. `tests/integration/test_frontend_dev_server.py`

## C4 endpoints

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
      "expected": "target style text",
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

Контракт валидации v0:

1. Ошибка для пустого датасета.
2. Ошибка для отсутствующего `case_id` или `input`.
3. Ошибка для дубликатов `case_id`.
4. Warning для пустого `expected`.

## C4 evaluation endpoints

`GET /api/arenas/{arena_id}/evaluation/state`

`POST /api/arenas/{arena_id}/evaluation/metrics/save`

`POST /api/arenas/{arena_id}/evaluation/evaluators/save`

`POST /api/arenas/{arena_id}/evaluation/budget/save`

`POST /api/arenas/{arena_id}/evaluation/validate`

`POST /api/arenas/{arena_id}/evaluation/save-version`

Validate-report status:

1. `ready` — ошибок нет.
2. `warnings` — только warning-issues.
3. `invalid` — есть error-issues.

## C5 optimizer endpoints

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

Launch guardrails проверяют:

1. C2 selected candidates + compile gate.
2. C4 assigned datasets.
3. C4 evaluation profile status.
4. Валидность C5 run_plan/budget/methods.
