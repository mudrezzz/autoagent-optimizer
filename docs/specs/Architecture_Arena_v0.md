# Architecture Arena v0

## Purpose

`Architecture Arena v0` добавляет турнирное сравнение 2-3 архитектур в одинаковом бюджете кейсов.

Текущий демо-домен Arena: `LinkedIn/Telegram style rewrite` с golden dataset и AI-pattern справочником.

Ключевые модули:

1. [optimizer/arena/tournament_schema.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/arena/tournament_schema.py)
2. [optimizer/arena/runner.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/arena/runner.py)
3. [optimizer/arena/run_tournament.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/arena/run_tournament.py)

## Tournament Contract v0

YAML-конфиг:

1. `version: arena_v0`
2. `dataset_file` — путь к golden dataset JSONL.
3. `execution_mode` — `expected_stub` или `runtime`.
4. `task_prefix` — префикс `task_id` для runtime режима.
5. `budget` — config-first политика бюджета.
6. `ranking` — config-first правила ранжирования.
7. `scoring` — config-first правила composite score.
8. `evaluator` — evaluator policy.
9. `participants` — список из 2-3 участников.

Участник:

1. `participant_id`
2. Ровно один источник: `dsl_file` или `graph_ir_file`
3. `stub_behavior` для deterministic режима:
   - `perfect`
   - `fail_sensitive`
   - `fail_all`

## Budget Policy

`budget` контракт:

1. `policy` — сейчас поддержан `equal_cases`.
2. `unit` — сейчас поддержан `cases`.
3. `selector`:
   - `head`
   - `random_seeded`
   - `hash_stable`
4. `limit` — сколько кейсов брать на участника (`0` = весь датасет).
5. `random_seed` — сид для `random_seeded` и `hash_stable`.

## Ranking Policy

`ranking.metrics` — упорядоченный список метрик с направлением сортировки.

Поддержанные метрики:

1. `pass_rate`
2. `passed`
3. `failed`
4. `participant_id`
5. `coverage`
6. `rule_violations_total`
7. `nodes_executed_total`
8. `avg_nodes_per_case`
9. `llm_calls_total`
10. `duration_ms_total`
11. `duration_ms_avg`
12. `p95_case_duration_ms`
13. `composite_score` (требует `scoring.enabled=true`)

Пример:

```yaml
ranking:
  metrics:
    - name: composite_score
      direction: desc
    - name: pass_rate
      direction: desc
    - name: passed
      direction: desc
    - name: failed
      direction: asc
    - name: participant_id
      direction: asc
```

## Scoring Policy

`scoring` контракт:

1. `enabled` — включить/выключить расчет `composite_score`.
2. `normalization` — стратегия нормализации (`minmax`).
3. `metrics[]` — список метрик composite score:
   - `name`
   - `direction` (`desc` или `asc`)
   - `weight` (положительный вес)

Пример:

```yaml
scoring:
  enabled: true
  normalization: minmax
  metrics:
    - name: pass_rate
      direction: desc
      weight: 0.6
    - name: rule_violations_total
      direction: asc
      weight: 0.3
    - name: duration_ms_avg
      direction: asc
      weight: 0.1
```

## Middle Metrics

Для каждого участника рассчитываются и публикуются `middle_metrics`:

1. `coverage` — доля кейсов с непустым текстовым ответом.
2. `rule_violations_total` — общее число нарушенных oracle-правил.
3. `nodes_executed_total` — сумма выполненных узлов по кейсам.
4. `avg_nodes_per_case` — среднее число выполненных узлов на кейс.
5. `llm_calls_total` — общее число LLM-вызовов по кейсам.
6. `duration_ms_total` — суммарная длительность кейсов.
7. `duration_ms_avg` — средняя длительность кейса.
8. `p95_case_duration_ms` — p95 латентности по кейсам.

Примечание: в `expected_stub` режиме runtime-поля (`nodes*`, `llm_calls*`, `duration*`) могут быть нулевыми,
так как детерминированный stub не исполняет реальный runtime pipeline.

## Evaluator Policy

`evaluator.mode`:

1. `rule_based_v0` — текущий rule-based oracle (`must_include`/`forbidden`).

## CLI

Стабильный deterministic запуск (для CI):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty
```

Live runtime запуск (для демо/ручной проверки):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
```

Full-budget запуск (весь dataset):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_full_v0.yaml --pretty
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_full_v0.yaml --pretty
```

Вывод включает:

1. `winner_id`
2. `ranking`
3. `participants[]` с `cases_total/passed/failed/pass_rate/middle_metrics/composite_score`
4. поля бюджета (`budget_policy`, `budget_unit`, `budget_selector`, `budget_limit`, `budget_seed`)
5. поля scoring (`scoring_enabled`, `scoring_normalization`, `scoring_policy`)
6. `ranking_policy` (фактически примененная конфигурация ранжирования)
7. `comparison` — секция сравнительных метрик для ranking и winner selection
8. `diagnostics` — секция диагностических сигналов по участникам:
   - `summary`
   - `stage_aggregates`
   - `top_bottlenecks`
   - `intervention_hints`

Для упаковки результата в читаемый артефакт используйте Evidence Pack CLI:

```powershell
python -m optimizer.evidence.generate_pack --arena-file .\examples\arena\support_tournament_ci_v0.yaml --out-dir .\tmp\evidence_pack --pretty
```

Dual contract:

1. `comparison` отвечает на вопрос "кто лучше".
2. `diagnostics` отвечает на вопрос "где ломается пайплайн и что чинить".

## Smoke

CI smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Full smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_full.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_full.ps1
```
