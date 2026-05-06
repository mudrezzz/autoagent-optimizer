# Architecture Arena v0

## Purpose

`Architecture Arena v0` добавляет турнирное сравнение 2-3 архитектур в одинаковом бюджете кейсов.

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
7. `evaluator` — evaluator policy.
8. `participants` — список из 2-3 участников.

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

Пример:

```yaml
ranking:
  metrics:
    - name: pass_rate
      direction: desc
    - name: passed
      direction: desc
    - name: failed
      direction: asc
    - name: participant_id
      direction: asc
```

## Evaluator Policy

`evaluator.mode`:

1. `rule_based_v0` — текущий rule-based oracle (`must_include`/`forbidden`).

## CLI

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
```

Вывод включает:

1. `winner_id`
2. `ranking`
3. `participants[]` с `cases_total/passed/failed/pass_rate`
4. поля бюджета (`budget_policy`, `budget_unit`, `budget_selector`, `budget_limit`, `budget_seed`)
5. `ranking_policy` (фактически примененная конфигурация ранжирования)

## Smoke

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```
