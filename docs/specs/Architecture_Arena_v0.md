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
4. `budget_policy: equal_cases`
5. `cases_limit` — общий лимит кейсов на каждого участника (`0` = весь датасет).
6. `participants` — список из 2-3 участников.

Участник:

1. `participant_id`
2. Ровно один источник: `dsl_file` или `graph_ir_file`
3. `stub_behavior` для deterministic режима:
   - `perfect`
   - `fail_sensitive`
   - `fail_all`

## Equal Budget Policy

В v0 используется политика `equal_cases`:

1. Выбирается единый набор кейсов (весь датасет или первые `cases_limit`).
2. Этот же набор запускается для каждого участника.
3. Таким образом бюджет сравнения одинаков по числу кейсов.

## Ranking Rules

Сортировка участников:

1. `pass_rate` (по убыванию),
2. `passed` (по убыванию),
3. `failed` (по возрастанию),
4. `participant_id` (лексикографически, как стабильный tie-break).

Первый в ранжировании — `winner_id`.

## CLI

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
```

Вывод включает:

1. `winner_id`
2. `ranking`
3. `participants[]` с `cases_total/passed/failed/pass_rate`
4. поля бюджета (`budget_policy`, `cases_budget`, `evaluated_records_total`)

## Smoke

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

