# Oracle Runner v0

## Purpose

`Oracle Runner v0` добавляет исполняемую deterministic проверку кейсов golden dataset.

Ключевые модули:

1. [optimizer/evaluation/oracle_rules.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/oracle_rules.py)
2. [optimizer/evaluation/oracle_runner.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/oracle_runner.py)
3. [optimizer/evaluation/run_oracle.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/run_oracle.py)

## Rule Contract v0

Поддерживаются правила `expected`:

1. `must_include: string[]` — каждая фраза должна встретиться в ответе.
2. `forbidden: string[]` — ни одна фраза не должна встретиться в ответе.

Кейс `passed`, если все правила `passed`.

## Execution Modes

1. `expected_stub` (по умолчанию):
   - deterministic режим для smoke/CI;
   - текст ответа строится из `expected.must_include`.
2. `runtime`:
   - реальный запуск workflow через renderer runtime.

## CLI

```powershell
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\direct_llm.yaml --dataset-file .\examples\datasets\golden_support_v1.jsonl --execution-mode expected_stub --pretty
```

Вывод summary:

1. `cases_total`
2. `passed`
3. `failed`
4. `pass_rate`
5. `execution_mode`

## Smoke

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_oracle.ps1
```

