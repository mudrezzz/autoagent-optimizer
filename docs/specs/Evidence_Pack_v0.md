# Evidence Pack v0

## Purpose

`Evidence Pack v0` превращает результат arena-турнира в два эксплуатационных артефакта:

1. `evidence_pack.json` для машинной обработки.
2. `evidence_pack.md` для быстрого чтения человеком.

Ключевой принцип: явное разделение `comparison` и `diagnostics`.

## Inputs

Поддерживаются два источника:

1. Arena YAML конфиг (`--arena-file`) с внутренним запуском турнира.
2. Уже сохраненный Arena JSON (`--arena-result-file`).

## Output Contract

`evidence_pack.json` содержит:

1. `tournament`:
   - `winner_id`, `challenger_id`, `ranking`,
   - `dataset_file`, `execution_mode`,
   - `cases_budget`, `dataset_records_total`, `evaluated_records_total`.
2. `comparison`:
   - `participants[].comparative_metrics`,
   - `winner_vs_challenger_diff[]` (explainable diff).
3. `diagnostics`:
   - `participants[].diagnostic_signals_by_stage`,
   - `participants[].top_bottlenecks`,
   - `participants[].intervention_hints`.
4. `recommendations`:
   - `for_challenger_priority_actions[]`.

`evidence_pack.md` дублирует ту же структуру в человекочитаемом виде.

## Explainable Diff Rules

Для пары `winner/challenger` diff строится минимум по:

1. `pass_rate`
2. `passed`
3. `failed`
4. `composite_score`
5. `rule_violations_total`
6. `duration_ms_avg`
7. `llm_calls_total`

Каждый diff-элемент содержит:

1. `metric`
2. `direction` (`asc|desc`)
3. `winner_value`
4. `challenger_value`
5. `delta_winner_minus_challenger`
6. `winner_advantage`
7. `interpretation`

## CLI

Генерация из arena-конфига:

```powershell
python -m optimizer.evidence.generate_pack --arena-file .\examples\arena\support_tournament_ci_v0.yaml --out-dir .\tmp\evidence_pack --pretty
```

Генерация из сохраненного arena-json:

```powershell
python -m optimizer.evidence.generate_pack --arena-result-file .\tmp\demo_results\arena_stylizer_ci_details.json --out-dir .\tmp\evidence_pack --pretty
```

Smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_evidence_pack.ps1
```

