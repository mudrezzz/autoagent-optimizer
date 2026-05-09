# ADR-0022: Evaluation Profile v0 Contract and Target Switch

- Status: Accepted
- Date: 2026-05-09
- Slice: I5.S1

## Context

После внедрения Arena v0 и dual-metrics модели оставалась проблема:

1. метрики и evaluator pipeline были частично зашиты в arena-конфиг,
2. не было отдельного task-level контракта оценки,
3. не было единой точки запуска одного и того же evaluation profile на `dsl_runtime` и `native_runtime`.

Для дальнейшего развития MetricOps/HITL и post-export loop нужен profile-driven слой.

## Decision

Принято:

1. ввести отдельный typed-контракт `Evaluation Profile v0`,
2. запускать profile через новый CLI `optimizer.evaluation.run_profile`,
3. поддержать переключение target:
   - `dsl_runtime`,
   - `native_runtime`,
4. сохранить совместимый выходной envelope с Arena (`comparison` + `diagnostics`).

## Consequences

Плюсы:

1. task-specific метрики, diagnostics и budget настраиваются конфигом без правки кода;
2. один и тот же профиль можно гонять на DSL-path и native-path;
3. появляется база для I5.S2 (pluggable evaluator adapters) без смены внешнего UX.

Минусы/ограничения v0:

1. evaluator chain ограничен `golden_oracle`;
2. native target пока выполняется через subprocess runtime и временный export участника;
3. budget поля кроме `cases_limit/selector` пока не применяются как hard gate.

## Implementation Notes

Реализовано:

1. `optimizer/evaluation/profile_schema.py`
2. `optimizer/evaluation/profile_io.py`
3. `optimizer/evaluation/profile_runner.py`
4. `optimizer/evaluation/run_profile.py`
5. examples profiles + test pyramid + smoke script.

## Follow-ups

1. I5.S2: вынести evaluator chain в adapter layer (`llm_judge`, `executable`, `render`).
2. I5.S4: использовать profile-run для post-export native re-benchmark loop.
