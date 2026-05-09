# Post-export Native Evaluation Loop v0

## Purpose

Зафиксировать непрерывный цикл оценки и улучшения после экспорта winner в standalone `native_agent`.

Цель: native artifact должен оставаться наблюдаемым и сравнимым объектом, а не “черным ящиком после экспорта”.

## Core Flow

```text
Select Winner
  -> Export Native Agent
  -> Benchmark Native Agent (golden / llm_judge / executable)
  -> Compare with Baseline
  -> Apply Regression Gates
  -> Promote or Rework
```

## Execution Targets

Evaluation profile должен поддерживать минимум:

1. `dsl_runtime`
2. `native_runtime`

Один и тот же benchmark pipeline должен уметь выполнять оба target и возвращать унифицированный result envelope.

## Unified Result Envelope

Каждый case-run возвращает:

1. `output_payload`
2. `trace_summary`
3. `node_events` (или совместимый событийный слой)
4. `cost/latency` агрегаты
5. `errors`

Это необходимо для сопоставимых comparative/diagnostic/regression отчетов.

## Evaluators

v0 pipeline поддерживает композиции:

1. `golden_oracle`
2. `llm_judge`
3. `executable`
4. (опционально) `render`

Profile определяет:

1. порядок evaluator chain,
2. budgets/limits,
3. aggregation rules.

## Regression Gates

Минимальный набор gate-правил:

1. quality floor (например pass_rate / judge_score не ниже baseline - delta).
2. cost ceiling (например llm_calls/cost не выше baseline + delta).
3. latency ceiling.
4. critical-failure gate (`errors_total`, hard rule violations).

Gate output:

1. `pass/fail`,
2. список нарушенных правил,
3. объяснимые значения baseline vs current.

## Baseline Policy

1. При экспорте champion фиксируется baseline snapshot:
   - profile id/version,
   - dataset slice id,
   - evaluator chain config,
   - aggregate metrics.
2. Любая модификация native agent сравнивается именно с этим baseline.

## Demo Contract

Для демо нужно показать:

1. экспорт native champion,
2. ручную модификацию native agent (контролируемую),
3. re-benchmark через тот же профиль,
4. решение gate: promote/rework.

## Scope Mapping to Roadmap

1. I5.S1: profile contract включает execution targets.
2. I5.S2: native runtime adapter в evaluator layer.
3. I5.S4: post-export benchmark loop CLI/report.
4. I5.S5: regression gate policy и promote decision.

