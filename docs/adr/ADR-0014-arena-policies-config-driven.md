# ADR-0014: Arena Policies Must Be Config-Driven

- Status: Accepted
- Date: 2026-05-06
- Slice: I4.S1
- Decision Makers: Project team
- Supersedes: ADR-0013 (частично, в части hardcoded policy)

## Context

В I3.S3 метрики ранжирования, tie-break и бюджетная логика были зафиксированы в коде runner.
Это противоречит принципу config-first, согласованному для AutoAgent Optimizer.

Нужно, чтобы правила сравнения архитектур и бюджет турнира задавались через YAML-конфиг,
а не через жестко зашитые `if`/`sorted(key=...)` в коде.

## Decision

1. Ввести policy-модели в `tournament_schema`:
   - `budget`
   - `ranking`
   - `evaluator`
2. Убрать fixed ranking key из runner и ранжировать строго по `ranking.metrics`.
3. Убрать fixed budget slicing и применять `budget.selector` + `budget.limit`.
4. Сохранить backward compatibility для legacy-полей `budget_policy`/`cases_limit` через миграцию в `budget`.

## Consequences

### Positive

1. Правила сравнения архитектур становятся прозрачными и управляемыми из конфига.
2. Снижается риск скрытых изменений качества из-за правок кода раннера.
3. Упрощается экспериментирование с ranking/budget без code changes.

### Negative / Trade-offs

1. Контракт конфига становится более сложным.
2. Появляется необходимость доп. валидации policy-конфига.
3. На v0 evaluator по-прежнему ограничен `rule_based_v0`.

## Verification

1. Unit: ranking policy и budget selector логика.
2. Integration: CLI успешно отражает config-driven policy в JSON output.
3. Full gate: `python -m pytest`.

## Links

1. `optimizer/arena/tournament_schema.py`
2. `optimizer/arena/runner.py`
3. `docs/specs/Architecture_Arena_v0.md`
