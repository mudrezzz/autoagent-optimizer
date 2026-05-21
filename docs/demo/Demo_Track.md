# Demo Track

## Purpose

Р”РµРјРѕ-С‚СЂРµРє РїРѕРєР°Р·С‹РІР°РµС‚ Р»СѓС‡С€РµРµ С‚РµРєСѓС‰РµРµ СЃРѕСЃС‚РѕСЏРЅРёРµ РїСЂРѕРµРєС‚Р° РЅР° РєР°Р¶РґРѕРј СЌС‚Р°РїРµ СЂР°Р·РІРёС‚РёСЏ.
РћРЅ СЂР°Р·РІРёРІР°РµС‚СЃСЏ СЃРёРЅС…СЂРѕРЅРЅРѕ СЃ roadmap, С‡С‚РѕР±С‹:

1. Р±С‹СЃС‚СЂРѕ РґРµРјРѕРЅСЃС‚СЂРёСЂРѕРІР°С‚СЊ РїСЂРѕРіСЂРµСЃСЃ;
2. РїСЂРѕРІРµСЂСЏС‚СЊ РёРЅС‚РµРіСЂР°С†РёСЋ РЅРѕРІС‹С… СЃР»Р°Р№СЃРѕРІ РЅР° Р¶РёРІРѕРј СЃС†РµРЅР°СЂРёРё;
3. РґР°РІР°С‚СЊ РїРѕРЅСЏС‚РЅС‹Р№ РІС…РѕРґ РЅРѕРІС‹Рј СЂР°Р·СЂР°Р±РѕС‚С‡РёРєР°Рј Рё СЃС‚РµР№РєС…РѕР»РґРµСЂР°Рј.

## Core Demo Scenario

Р‘Р°Р·РѕРІС‹Р№ СЃС†РµРЅР°СЂРёР№ РґРµРјРѕ (РёР· MVP-РІРµСЂС‚РёРєР°Р»Рё РўР—):

`AI style rewrite for LinkedIn/Telegram posts`

РџРѕС‡РµРјСѓ РІС‹Р±СЂР°РЅ:

1. РјРѕР¶РЅРѕ Р±С‹СЃС‚СЂРѕ СѓРІРёРґРµС‚СЊ Р»РѕРіРёС‡РµСЃРєРёРµ РїСЂРѕРІР°Р»С‹ РЅР° РїРѕРЅСЏС‚РЅРѕРј С‡РµР»РѕРІРµРєСѓ СЂРµР·СѓР»СЊС‚Р°С‚Рµ;
2. РјРµС‚СЂРёРєРё СЏРІРЅРѕ task-specific (СЃРјС‹СЃР», СЌРЅРµСЂРіРёСЏ, С„Р°РєС‚С‹, РґР»РёРЅР°, AI-РїР°С‚С‚РµСЂРЅС‹);
3. РµСЃС‚РµСЃС‚РІРµРЅРЅРѕ РїРѕРєР°Р·С‹РІР°РµС‚ СЂР°Р·РЅРёС†Сѓ comparative vs diagnostic СЃР»РѕРµРІ;
4. С…РѕСЂРѕС€Рѕ РїРѕРґС…РѕРґРёС‚ РґР»СЏ Р±СѓРґСѓС‰РµРіРѕ MetricOps + HITL С†РёРєР»Р°.

## Secondary Demo Scenario

Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Р№ СЃС†РµРЅР°СЂРёР№:

`Complex PDF/OCR extraction -> structured database rows`

Р•РіРѕ СЃРѕС…СЂР°РЅСЏРµРј РєР°Рє СЂР°СЃС€РёСЂРµРЅРЅС‹Р№ enterprise-РєРµР№СЃ РґР»СЏ СЃР»РµРґСѓСЋС‰РёС… MVP.

## Demo Evolution By Iteration

### Stage D0 (I1) - Spec Demo

Р§С‚Рѕ РїРѕРєР°Р·С‹РІР°РµРј СЃРµР№С‡Р°СЃ:

1. DSL v0 СЃРїРµС†РёС„РёРєР°С†РёСЏ (`examples/dsl/*.yaml`);
2. Graph IR v0 СЃРїРµС†РёС„РёРєР°С†РёСЏ (`examples/graph_ir/*.json`);
3. compile path DSL -> Graph IR;
4. smoke-РІР°Р»РёРґР°С†РёСЏ РѕР±РѕРёС… СѓСЂРѕРІРЅРµР№.

РљРѕРјР°РЅРґС‹:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_dsl.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_graph_ir.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_compile_dsl_to_ir.ps1
```

### Stage D1 (I2) - Runtime Demo

Р§С‚Рѕ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµРј:

1. РєРѕРјРїРёР»СЏС†РёСЏ DSL -> IR;
2. СЂРµРЅРґРµСЂ IR -> РёСЃРїРѕР»РЅСЏРµРјС‹Р№ workflow;
3. invoke path РЅР° РЅРµСЃРєРѕР»СЊРєРёС… СЃС†РµРЅР°СЂРёСЏС… (`direct_llm`, `hitl_gate low/high risk`);
4. СЂРµР°Р»СЊРЅС‹Р№ OpenRouter-РІС‹Р·РѕРІ РІ LLM СѓР·Р»Р°С… РїСЂРё РЅР°Р»РёС‡РёРё `OPENROUTER_API_KEY`;
5. РіРµРЅРµСЂР°С†РёСЏ РєРѕРґРѕРІРѕРіРѕ Р°СЂС‚РµС„Р°РєС‚Р° Р°РіРµРЅС‚Р° (`DSL -> generated package -> generated runner`).
6. checkpoint/resume РїСѓС‚СЊ (`invoke -> checkpoint -> resume`) РїРѕ `task_id`.

РџРѕРєР° РІ СЂР°Р±РѕС‚Рµ:

1. СЂР°СЃС€РёСЂРµРЅРёРµ trace РІ СЃС‚РѕСЂРѕРЅСѓ checkpoint-aware run history.

РљРѕРјР°РЅРґС‹:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_agent_code.ps1
```

Р’ runtime РІС‹РІРѕРґРµ РѕР¶РёРґР°РµРј РїРѕР»СЏ `node_events` Рё `trace_summary`.

### Stage D2 (I3) - Evaluation Demo

Р§С‚Рѕ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµРј:

1. РІР°Р»РёРґР°С†РёСЋ golden dataset JSONL С‡РµСЂРµР· typed loader Рё CLI;
2. РёСЃРїРѕР»РЅСЏРµРјС‹Р№ oracle-РїСЂРѕРіРѕРЅ РїРѕ golden dataset (`expected_stub` РґР»СЏ deterministic smoke/CI);
3. summary pass/fail (`cases_total/passed/failed/pass_rate`) Рё РєРѕСЂСЂРµРєС‚РЅС‹Р№ exit code.

РљРѕРјР°РЅРґС‹:

```powershell
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\style_direct_llm.yaml --dataset-file .\examples\datasets\golden_linkedin_stylizer_v1.jsonl --execution-mode expected_stub --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_oracle.ps1
```

Р§С‚Рѕ СѓР¶Рµ РґРѕР±Р°РІР»РµРЅРѕ РІ D2:

1. equal-budget tournament РјРµР¶РґСѓ 2-3 Р°СЂС…РёС‚РµРєС‚СѓСЂР°РјРё (I3.S3);
2. ranking + winner СЃ РїСЂРѕР·СЂР°С‡РЅС‹Рј tie-break РєРѕРЅС‚СЂР°РєС‚РѕРј;
3. CLI Рё smoke-РєРѕРјР°РЅРґР° РґР»СЏ РІРѕСЃРїСЂРѕРёР·РІРѕРґРёРјРѕРіРѕ СЃСЂР°РІРЅРµРЅРёСЏ.

РљРѕРјР°РЅРґС‹ Arena:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live РєРѕРјР°РЅРґС‹ Arena:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Decision-profile РєРѕРјР°РЅРґС‹ Arena (РґР»СЏ Р±РѕР»РµРµ РЅР°РґРµР¶РЅРѕРіРѕ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅРѕРіРѕ СЂРµС€РµРЅРёСЏ):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --pretty
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_decision_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_decision.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_decision.ps1
```

Full-budget РєРѕРјР°РЅРґС‹ Arena (РґРѕСЂРѕР¶Рµ, РґР»СЏ РєРѕРЅС‚СЂРѕР»СЊРЅС‹С… РїСЂРѕРіРѕРЅРѕРІ):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_full_v0.yaml --pretty
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_full_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_full.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_full.ps1
```

Р§С‚Рѕ СѓР¶Рµ РґРѕР±Р°РІР»РµРЅРѕ РІ D3:

1. `middle_metrics` РїРѕ РєР°Р¶РґРѕРјСѓ СѓС‡Р°СЃС‚РЅРёРєСѓ (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`);
2. config-driven `scoring` policy СЃ РІРµСЃР°РјРё/РЅР°РїСЂР°РІР»РµРЅРёСЏРјРё;
3. `composite_score` Рё `score_breakdown` РІ РёС‚РѕРіРѕРІРѕРј РѕС‚С‡РµС‚Рµ С‚СѓСЂРЅРёСЂР°.
4. СЂР°СЃС€РёСЂРµРЅРЅС‹Р№ stylizer dataset (12 РґР»РёРЅРЅС‹С… РєРµР№СЃРѕРІ) + СЂР°Р·РґРµР»СЊРЅС‹Рµ smoke/full budget РїСЂРѕС„РёР»Рё.
5. Evidence Pack v0 (`evidence_pack.json` + `evidence_pack.md`) СЃ СЂР°Р·РґРµР»РµРЅРёРµРј `comparison` Рё `diagnostics`.
6. explainable winner/challenger diff Рё РїСЂРёРѕСЂРёС‚РµС‚РЅС‹Рµ СЂРµРєРѕРјРµРЅРґР°С†РёРё РґР»СЏ challenger.
7. СЂР°Р·РґРµР»РµРЅРёРµ run-policy:
   - `smoke-live`: cheap model + 4 РєРµР№СЃР°,
   - `decision-live`: quality model + 8 РєРµР№СЃРѕРІ (`hash_stable`).

РЎР»РµРґСѓСЋС‰РёР№ С€Р°Рі:

1. Native-first champion bundle default switch (I4.S8).

### Stage D3 (I4) - Champion Demo

Р§С‚Рѕ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµРј:

1. С„РѕСЂРјРёСЂРѕРІР°РЅРёРµ Evidence Pack;
2. champion/challenger СЃСЂР°РІРЅРµРЅРёРµ;
3. export champion bundle СЃ `diagnostic_map.json`, `winner_graph_ir.json` Рё `generated_agent/*`;
4. reproducible handoff С‡РµСЂРµР· `bundle_manifest.json`.

РљРѕРјР°РЅРґС‹:

```powershell
python -m optimizer.champion.export_bundle --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_export_champion_bundle.ps1
```

### Stage D4 (I5) - Evaluation Fabric Demo

РџР»Р°РЅ РїРѕРєР°Р·Р°:

1. profile-driven РѕС†РµРЅРєР° РґР»СЏ РґРІСѓС… СЂР°Р·РЅС‹С… Р·Р°РґР°С‡:
   - OCR/support,
   - style rewrite social post.
2. РїРµСЂРµРєР»СЋС‡РµРЅРёРµ evaluator methods Р±РµР· РїСЂР°РІРєРё РєРѕРґР° (`golden_oracle`, `llm_judge`, `executable`, `render`).
3. metric-crafting agent draft + HITL approve РґР»СЏ Р°РєС‚РёРІР°С†РёРё profile.
4. post-export native re-benchmark: РїСЂРѕРіРѕРЅ native champion РЅР° С‚РµС… Р¶Рµ evaluation profiles, СЃСЂР°РІРЅРµРЅРёРµ СЃ DSL baseline Рё gate-СЂРµС€РµРЅРёРµ (`promote` / `rework`).

Р§С‚Рѕ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµРј:

1. typed `Evaluation Profile v0` РґР»СЏ stylizer/ocr РєРµР№СЃРѕРІ;
2. Р·Р°РїСѓСЃРє РѕРґРЅРѕРіРѕ profile РЅР° РґРІСѓС… target:
   - `dsl_runtime`,
   - `native_runtime`;
3. unified profile-run envelope СЃ `comparison` + `diagnostics`.
4. native preflight v0: РґРѕ Р·Р°РїСѓСЃРєР° `native_runtime` СЃС‚СЂРѕРёС‚СЃСЏ compatibility report РїРѕ participants.
5. canonical stylizer profile (`stylizer_profile_ci_v0`) СѓСЃРїРµС€РЅРѕ РІС‹РїРѕР»РЅСЏРµС‚СЃСЏ РЅР° `native_runtime` Р±РµР· workaround policy.

РљРѕРјР°РЅРґС‹:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile_native_preflight.ps1
```

Ожидаемо после `I4.S6`:

1. `dsl_runtime` команда должна проходить стабильно.
2. `native_runtime` canonical stylizer профиль должен проходить успешно.
3. `native_runtime` на профиле с `tool`-узлами должен проходить preflight и запускаться без `native_compatibility_preflight_failed`.

### Stage D3.5 (I4.S4-I4.S8) - Native Export Independence Demo

РџР»Р°РЅ РїРѕРєР°Р·Р°:

1. export native standalone Р°РіРµРЅС‚Р° РЅР° `langgraph-dai` Р±РµР· РёРјРїРѕСЂС‚РѕРІ `optimizer.*`;
2. Р·Р°РїСѓСЃРє standalone runtime РёР· bundle РІ РѕС‚РґРµР»СЊРЅРѕРј РѕРєСЂСѓР¶РµРЅРёРё;
3. parity report `dsl_vs_native` РїРѕ СЃС‚СЂСѓРєС‚СѓСЂРЅС‹Рј СЃРёРіРЅР°Р»Р°Рј РёСЃРїРѕР»РЅРµРЅРёСЏ;
4. РїРµСЂРµРєР»СЋС‡РµРЅРёРµ champion bundle default РЅР° native target.

Р§С‚Рѕ СѓР¶Рµ РїРѕРєР°Р·С‹РІР°РµРј:

1. champion bundle СЃРѕРґРµСЂР¶РёС‚ `native_agent/` standalone runtime РїР°РєРµС‚;
2. smoke СЃС†РµРЅР°СЂРёР№ Р·Р°РїСѓСЃРєР°РµС‚ standalone native runner РёР· bundle;
3. `parity_report.json` РІРєР»СЋС‡Р°РµС‚ `native_runtime_smoke`.

## Demo Contract For Every Slice

Р”Р»СЏ РєР°Р¶РґРѕРіРѕ СЃР»Р°Р№СЃР° РѕР±СЏР·Р°С‚РµР»СЊРЅРѕ:

1. РѕР±РЅРѕРІРёС‚СЊ, С‡С‚Рѕ РёР·РјРµРЅРёР»РѕСЃСЊ РІ РґРµРјРѕ;
2. СЃРѕС…СЂР°РЅРёС‚СЊ/РґРѕР±Р°РІРёС‚СЊ runnable РєРѕРјР°РЅРґСѓ РёР»Рё СЃС†РµРЅР°СЂРёР№;
3. Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ РѕР¶РёРґР°РµРјС‹Р№ СЂРµР·СѓР»СЊС‚Р°С‚ (С‡С‚Рѕ СѓРІРёРґРёС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ);
4. СЃРёРЅС…СЂРѕРЅРёР·РёСЂРѕРІР°С‚СЊ СЃСЃС‹Р»РєРё РІ `README` Рё `Roadmap` РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё.

## Current Demo Status

- Active stage: `D4 bootstrap (I5 evaluation profile v0)`
- Demo readiness: `Yellow` (native-first bundle default pending in I4.S8)
- Next demo milestone: `D3.5 native-first bundle default` (`I4.S8`)

