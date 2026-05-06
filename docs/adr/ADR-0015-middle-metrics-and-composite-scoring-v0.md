# ADR-0015: Middle Metrics And Composite Scoring Must Be Config-Driven

- Status: Accepted
- Date: 2026-05-06
- Slice: I4.S1
- Decision Makers: Project team
- Supersedes: None

## Context

После I3.S3 базовое сравнение архитектур опиралось только на `pass_rate/passed/failed`.
Для реального отбора champion этого недостаточно: нужны промежуточные сигналы качества, стоимости и латентности.

Также важно сохранить принцип config-first:
формула итогового сравнения не должна быть зашита в коде раннера.

## Decision

1. Добавить слой `middle_metrics`, рассчитываемый из oracle-результатов по кейсам:
   - `coverage`
   - `rule_violations_total`
   - `nodes_executed_total`
   - `avg_nodes_per_case`
   - `llm_calls_total`
   - `duration_ms_total`
   - `duration_ms_avg`
   - `p95_case_duration_ms`
2. Добавить `scoring` policy в контракт Arena:
   - `enabled`
   - `normalization` (`minmax`)
   - `metrics[]` (`name`, `direction`, `weight`)
3. Рассчитывать `composite_score` и `score_breakdown` по policy, без hardcoded формулы.
4. Разрешить ranking по `composite_score` только при `scoring.enabled=true`.

## Consequences

### Positive

1. Сравнение архитектур становится многокритериальным и прозрачным.
2. Весовые коэффициенты и приоритеты метрик управляются YAML-конфигом.
3. Можно безопасно расширять критерии без переписывания core runner.

### Negative / Trade-offs

1. Усложняется турнирный JSON-отчет и контракт конфига.
2. Появляется риск некорректной интерпретации весов пользователем.
3. На v0 нормализация ограничена `minmax`.

## Verification

1. Unit: расчет middle-метрик и composite score.
2. Integration: CLI-турнир отдает `middle_metrics`, `scoring_policy`, `composite_score`.
3. Full gate: `python -m pytest`.

## Links

1. `optimizer/metrics/middle_metrics.py`
2. `optimizer/arena/tournament_schema.py`
3. `optimizer/arena/runner.py`
4. `docs/specs/Architecture_Arena_v0.md`
