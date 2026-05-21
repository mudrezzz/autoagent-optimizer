# Evaluation Profile v0

## Purpose

`Evaluation Profile` Р·Р°РґР°РµС‚ РєРѕРЅС„РёРі РѕС†РµРЅРєРё РїРѕРґ РєРѕРЅРєСЂРµС‚РЅС‹Р№ task type:

1. РєР°РєРёРµ comparative-РјРµС‚СЂРёРєРё СѓС‡Р°СЃС‚РІСѓСЋС‚ РІ ranking,
2. РєР°РєРёРµ diagnostic-СЃРёРіРЅР°Р»С‹ СЃРѕР±РёСЂР°СЋС‚СЃСЏ РґР»СЏ root-cause Р°РЅР°Р»РёР·Р°,
3. РєР°РєРѕР№ evaluator chain РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ,
4. РєР°РєРѕР№ execution target Р·Р°РїСѓСЃРєР°РµС‚СЃСЏ (`dsl_runtime` РёР»Рё `native_runtime`),
5. РєР°РєРѕР№ Р±СЋРґР¶РµС‚ РїСЂРёРјРµРЅСЏРµС‚СЃСЏ Рє РїСЂРѕРіРѕРЅСѓ.

## Scope (I5.S1)

Р’ СЌС‚РѕРј СЃР»Р°Р№СЃРµ СЂРµР°Р»РёР·РѕРІР°РЅРѕ:

1. typed РєРѕРЅС‚СЂР°РєС‚ profile (`optimizer/evaluation/profile_schema.py`),
2. YAML loader + validator (`optimizer/evaluation/profile_io.py`),
3. CLI `python -m optimizer.evaluation.run_profile`,
4. orchestration runner РґР»СЏ target-РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ (`optimizer/evaluation/profile_runner.py`),
5. examples profiles РґР»СЏ РґРІСѓС… task types.

Р’ `v0` evaluator chain РѕРіСЂР°РЅРёС‡РµРЅ `golden_oracle`.
Р Р°СЃС€РёСЂСЏРµРјС‹Рµ evaluator adapters (`llm_judge`, `executable`, `render`) РёРґСѓС‚ РІ `I5.S2`.

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

РџРѕРґРґРµСЂР¶РєР° target РІ `v0`:

1. `dsl_runtime`
   - РёСЃРїРѕР»СЊР·СѓРµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ Arena runtime РїСѓС‚СЊ,
   - `dsl_execution_mode` Р±РµСЂРµС‚СЃСЏ РёР· profile (`expected_stub`/`runtime`).
2. `native_runtime`
   - РґР»СЏ РєР°Р¶РґРѕРіРѕ СѓС‡Р°СЃС‚РЅРёРєР° РїСЂРѕС„РёР»СЊРЅРѕРіРѕ С‚СѓСЂРЅРёСЂР° РєРѕРјРїРёР»РёСЂСѓРµС‚СЃСЏ Graph IR,
   - СѓС‡Р°СЃС‚РЅРёРє СЌРєСЃРїРѕСЂС‚РёСЂСѓРµС‚СЃСЏ РІРѕ РІСЂРµРјРµРЅРЅС‹Р№ standalone native runtime,
   - РѕС†РµРЅРєР° РёРґРµС‚ С‡РµСЂРµР· С‚РѕС‚ Р¶Рµ oracle pipeline Рё С‚Сѓ Р¶Рµ budget/ranking/scoring РїРѕР»РёС‚РёРєСѓ.

## Known Limitation (2026-05-21)

Для `native_runtime` в `v0` теперь покрыты node kinds: `llm`, `deterministic`, `tool`, `validator`, `hitl_gate`.

Preflight в `strict_preflight_v0` режиме сохраняется как fail-fast слой для реально несовместимых кейсов:

1. broken source resolution (битый `dsl_file`/`graph_ir_file`);
2. compile failures при DSL -> Graph IR;
3. unresolved runtime bindings для component refs.

Статус по итерациям:

1. `I5.S2a` — выполнено: compatibility preflight до native запуска;
2. `I4.S6a` — выполнено: canonical DSL->native parity для stylizer профиля;
3. `I4.S6` — выполнено: native tool binding layer;
4. следующий шаг: `I4.S7` (DSL-vs-native parity harness + CI gate).

## CLI

Р—Р°РїСѓСЃРє profile-run:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
```

Р•СЃР»Рё `--target` РЅРµ Р·Р°РґР°РЅ, РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ `default_target` РёР· profile.

## Output Envelope

CLI РІРѕР·РІСЂР°С‰Р°РµС‚:

1. profile meta (`profile_id`, `task_type`, `execution_target`),
2. evaluator/metrics/budget contract snapshot,
3. `preflight` СЃРµРєС†РёСЋ (РґР»СЏ `native_runtime` вЂ” structured compatibility report),
4. `result` РІ СЃРѕРІРјРµСЃС‚РёРјРѕРј С„РѕСЂРјР°С‚Рµ Arena (`comparison`, `diagnostics`, `participants`, `winner_id`).

## Example Profiles

1. `examples/profiles/stylizer_profile_ci_v0.yaml`
2. `examples/profiles/ocr_support_profile_ci_v0.yaml`

## Tests

РџРѕРєСЂС‹С‚РёРµ СЃР»Р°Р№СЃР°:

1. unit: `tests/unit/test_evaluation_profile_schema.py`
2. integration: `tests/integration/test_evaluation_profile_cli.py`
3. e2e: `tests/e2e/test_evaluation_profile_smoke_script.py`
