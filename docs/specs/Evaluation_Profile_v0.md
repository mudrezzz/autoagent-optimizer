# Evaluation Profile v0

## Purpose

`Evaluation Profile` задает правила оценки **под конкретный кейс**, а не глобально для всех задач.

Профиль решает две проблемы:

1. Метрики различаются между задачами и должны быть конфигурируемыми.
2. Методы оценки должны быть расширяемыми (не только golden dataset).

## Design Principles

1. `Config-first`: состав метрик и оценщиков задается YAML/JSON профилем.
2. `Dual Metrics`: разделяем comparative и diagnostic слои.
3. `Pluggable Evaluators`: новые оценщики подключаются через adapter interface.
4. `HITL-by-default for metric changes`: изменение профиля метрик проходит подтверждение.

## Profile Structure (Concept)

1. `profile_id`, `task_type`, `version`
2. `comparative_metrics[]`
   - `metric_id`
   - `direction` (`asc`/`desc`)
   - `weight`
   - `source` (`golden_oracle`, `llm_judge`, `runtime_trace`, `executable`, ...)
3. `diagnostic_signals[]`
   - `signal_id`
   - `stage_scope` (`retrieve`, `rerank`, `synthesize`, `validate`, `tool_call`, ...)
   - `aggregation`
4. `evaluators[]`
   - `evaluator_type`
   - `config`
   - `budget`
5. `gates[]`
   - обязательные минимумы/максимумы перед продвижением champion
6. `normalization` и `scoring_policy`

## Evaluator Adapter Model

Каждый evaluator реализует единый контракт:

1. `prepare(context) -> evaluator_session`
2. `evaluate(case_input, candidate_output) -> evaluator_result`
3. `aggregate(results[]) -> metrics/signals`

Базовые evaluator types v0:

1. `golden_oracle` — сравнение с эталоном.
2. `llm_judge` — LLM-as-a-judge по рубрике.
3. `executable` — запуск тестов/кода/валидаторов.
4. `render` — проверка рендера/артефактов.
5. `runtime_trace` — оценка поведения из trace/events.

## Metric-Crafting Agent + HITL

Построение/эволюция профиля метрик оформляется как отдельный agent workflow:

1. Агент предлагает draft метрики и evaluator composition.
2. Платформа генерирует expected impact + риски.
3. Человек подтверждает/редактирует профиль (HITL checkpoint).
4. После approval профиль активируется в турнире.

Без HITL подтверждения профиль не меняет production ranking.

## Example Task Types

1. `style_rewrite_social_post` (LinkedIn/Telegram):
   - comparative:
     - смысловая сохранность,
     - естественность стиля,
     - сохранение длины,
     - retention фактов/пруфов.
   - diagnostics:
     - потеря фабулы,
     - потеря энергии текста,
     - leakage AI-паттернов.

2. `code_agent_generation`:
   - comparative:
     - pass_rate тестов,
     - runtime latency,
     - cost budget.
   - diagnostics:
     - ошибки на stage compile/test/run.

## Integration Plan

1. I5.S1: контракт профиля + валидация.
2. I5.S2: evaluator adapters и unified aggregation path.
3. I5.S3: metric-crafting agent с HITL checkpoint.
