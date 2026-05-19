# Evaluation Profile v0

## Purpose

`Evaluation Profile` задает конфиг оценки под конкретный task type:

1. какие comparative-метрики участвуют в ranking,
2. какие diagnostic-сигналы собираются для root-cause анализа,
3. какой evaluator chain используется,
4. какой execution target запускается (`dsl_runtime` или `native_runtime`),
5. какой бюджет применяется к прогону.

## Scope (I5.S1)

В этом слайсе реализовано:

1. typed контракт profile (`optimizer/evaluation/profile_schema.py`),
2. YAML loader + validator (`optimizer/evaluation/profile_io.py`),
3. CLI `python -m optimizer.evaluation.run_profile`,
4. orchestration runner для target-переключения (`optimizer/evaluation/profile_runner.py`),
5. examples profiles для двух task types.

В `v0` evaluator chain ограничен `golden_oracle`.
Расширяемые evaluator adapters (`llm_judge`, `executable`, `render`) идут в `I5.S2`.

## YAML Contract

```yaml
version: evaluation_profile_v0
profile_id: stylizer_profile_ci_v0
task_type: style_rewrite_social_post
supported_targets: [dsl_runtime, native_runtime]
default_target: dsl_runtime
dataset_file: ../datasets/golden_linkedin_stylizer_v1.jsonl
dsl_execution_mode: expected_stub
task_prefix: profile-stylizer-ci

budget:
  cases_limit: 4
  selector: head
  random_seed: 42
  max_llm_calls: 0
  max_input_tokens: 0
  max_output_tokens: 0
  max_usd: 0.0
  max_wall_time_sec: 0

evaluators:
  - evaluator_type: golden_oracle
    config: {}
    budget: {}

comparative_metrics:
  - metric_id: pass_rate
    direction: desc
    weight: 0.6
    source: golden_oracle
  - metric_id: duration_ms_avg
    direction: asc
    weight: 0.4
    source: runtime_trace

diagnostic_signals:
  - signal_id: synthesize_bottleneck
    stage_scope: synthesize
    aggregation: avg

participants:
  - participant_id: candidate_a
    dsl_file: ../dsl/style_direct_llm.yaml
    stub_behavior: perfect
  - participant_id: candidate_b
    dsl_file: ../dsl/style_pattern_cleaner.yaml
    stub_behavior: fail_sensitive
```

## Execution Targets

Поддержка target в `v0`:

1. `dsl_runtime`
   - использует существующий Arena runtime путь,
   - `dsl_execution_mode` берется из profile (`expected_stub`/`runtime`).
2. `native_runtime`
   - для каждого участника профильного турнира компилируется Graph IR,
   - участник экспортируется во временный standalone native runtime,
   - оценка идет через тот же oracle pipeline и ту же budget/ranking/scoring политику.

## Known Limitation (2026-05-19)

Для `native_runtime` в `v0` действует ограничение native exporter capability:

1. поддерживаются только node kinds: `llm`, `deterministic`, `validator`;
2. профили с `hitl`/другими неподдержанными узлами блокируются preflight-ом в `strict_preflight_v0` режиме.

Статус исправления:

1. `I5.S2a` — выполнено: compatibility preflight до native запуска;
2. `I5.S2b` — в плане: formal degradation policy (`strict` / `skip_unsupported`) с прозрачным отчетом.

## CLI

Запуск profile-run:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
```

Если `--target` не задан, используется `default_target` из profile.

## Output Envelope

CLI возвращает:

1. profile meta (`profile_id`, `task_type`, `execution_target`),
2. evaluator/metrics/budget contract snapshot,
3. `preflight` секцию (для `native_runtime` — structured compatibility report),
4. `result` в совместимом формате Arena (`comparison`, `diagnostics`, `participants`, `winner_id`).

## Example Profiles

1. `examples/profiles/stylizer_profile_ci_v0.yaml`
2. `examples/profiles/ocr_support_profile_ci_v0.yaml`

## Tests

Покрытие слайса:

1. unit: `tests/unit/test_evaluation_profile_schema.py`
2. integration: `tests/integration/test_evaluation_profile_cli.py`
3. e2e: `tests/e2e/test_evaluation_profile_smoke_script.py`
