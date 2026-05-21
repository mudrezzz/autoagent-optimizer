# DSL-vs-Native Parity Harness v0

## Purpose

Этот документ фиксирует контракт структурной parity-проверки между:

1. `dsl_runtime` path (Graph IR через renderer),
2. `native_runtime` path (standalone export на `langgraph-dai`).

Цель: ловить архитектурный drift в CI без зависимости от вариативности текстов LLM.

## CLI

```powershell
python -m optimizer.parity.run --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --cases-limit 1 --fail-on-mismatch --pretty
```

Опции:

1. `--cases-limit` — сколько dataset-кейсов проверять на participant.
2. `--participant-id` — фильтр по участникам (можно передавать несколько раз).
3. `--out-file` — сохранить JSON отчет на диск.
4. `--fail-on-mismatch` — вернуть exit code `1` при любом parity mismatch.

## Structural Checks v0

Для каждого `participant` и каждого выбранного `case_id` проверяются:

1. `executed_nodes` equality;
2. `skipped_nodes` equality;
3. `node_output_keys` equality (только форма выходов, не значения текста);
4. `errors` equality;
5. `trace_topology` equality (`node_id`, `status`, `next_nodes`).

## Determinism Policy

Parity run выполняется в режиме `mock_llm_for_stability`:

1. `OPENROUTER_API_KEY` временно отключается;
2. сравнение фокусируется на структурных сигналах;
3. текстовые отличия LLM не являются критерием parity.

## Output Contract

`dsl_native_parity_v0` отчет содержит:

1. `profile_id`, `mode`, `passed`;
2. агрегаты `participants_total/passed/failed`;
3. для каждого `participant`:
   - `cases_total/cases_passed`,
   - `case_results[]` с `checks` и `mismatches`.

## CI Gate Contract

Для CI используется `--fail-on-mismatch`:

1. если `report.passed=true` -> exit code `0`;
2. если есть mismatch -> exit code `1`.

