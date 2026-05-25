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
