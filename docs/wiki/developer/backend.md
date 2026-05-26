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
