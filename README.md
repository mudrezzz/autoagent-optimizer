# AutoAgent Optimizer

OSS-first РїР»Р°С‚С„РѕСЂРјР° РґР»СЏ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅРѕРіРѕ РїРѕРёСЃРєР°, white-box РѕС†РµРЅРєРё Рё РёС‚РµСЂР°С‚РёРІРЅРѕР№ РѕРїС‚РёРјРёР·Р°С†РёРё compound AI systems.

## Current Status

- `Phase`: MVP-2 transition (product realignment + evaluation fabric)
- `Iteration`: Roadmap v3 - vertical product slices
- `Overall`: In Progress (V2.3.S1 + V2.3.S1a done, product capabilities C1-C6 in rollout)
- `Next Slice`: V2.3.S2 Project Chat brief-to-candidates v0

РџРѕРґСЂРѕР±РЅС‹Р№ СЃС‚Р°С‚СѓСЃ:

- [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
- [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
- [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md)
- [ADR Index](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)
- [Project Operating Model](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)
- [Executable Slice Backlog](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)
- [Demo Track](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)

## Project Rules

1. Р Р°Р·РІРёРІР°РµРј РїСЂРѕРґСѓРєС‚ РјР°Р»С‹РјРё СЃР»Р°Р№СЃР°РјРё, РєР°Р¶РґС‹Р№ СЃР»Р°Р№СЃ РґРѕР»Р¶РµРЅ РґР°РІР°С‚СЊ РїСЂРѕРІРµСЂСЏРµРјС‹Р№ РёРЅРєСЂРµРјРµРЅС‚.
2. Р’СЃРµ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Рµ СЂРµС€РµРЅРёСЏ С„РёРєСЃРёСЂСѓСЋС‚СЃСЏ С‡РµСЂРµР· ADR/ARD РґРѕ РёР»Рё РІРјРµСЃС‚Рµ СЃ СЂРµР°Р»РёР·Р°С†РёРµР№.
3. `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` РІСЃРµРіРґР° Р°РєС‚СѓР°Р»СЊРЅС‹ РїРѕСЃР»Рµ РєР°Р¶РґРѕРіРѕ СЃР»Р°Р№СЃР°.
4. РќРѕРІС‹Р№ СЂР°Р·СЂР°Р±РѕС‚С‡РёРє РґРѕР»Р¶РµРЅ Р·Р° 10-15 РјРёРЅСѓС‚ РїРѕРЅСЏС‚СЊ С‚РµРєСѓС‰РёР№ СЃС‚Р°С‚СѓСЃ Рё РІР·СЏС‚СЊ СЃР»РµРґСѓСЋС‰РёР№ СЃР»Р°Р№СЃ.
5. РљР°Р¶РґС‹Р№ СЃР»Р°Р№СЃ Р·Р°РІРµСЂС€Р°РµС‚СЃСЏ РѕС‚РґРµР»СЊРЅС‹Рј git commit.
6. Р Р°Р·РІРёС‚РёРµ РёРґРµС‚ РєРѕРЅС†РµРЅС‚СЂРёС‡РµСЃРєРёРјРё MVP-РєСЂСѓРіР°РјРё: MVP-1 -> MVP-2 -> MVP-3.
7. Р”РµРјРѕ СЂР°Р·РІРёРІР°РµС‚СЃСЏ СЃРёРЅС…СЂРѕРЅРЅРѕ СЃ С„СѓРЅРєС†РёРѕРЅР°Р»РѕРј Рё РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ РЅР° РєР°Р¶РґРѕРј СЃР»Р°Р№СЃРµ.
8. Каждый новый backend-инкремент должен стать проверяемым через frontend в том же слайсе.
9. Весь frontend строго следует `design_system` (tokens, типографика, компоненты, voice) без локальных визуальных отклонений.
10. UX-композиция frontend строится по North Star референсу [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png) и правилам из [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md).

## Design System Compliance

`design_system` — единственный источник истины для визуального/контентного языка интерфейса.

Обязательные правила:

1. Всегда использовать токены из [colors_and_type.css](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/colors_and_type.css), а не произвольные цвета/радиусы/тени.
2. Использовать только бренд-шрифты `Geist` и `Geist Mono` по scale из дизайн-системы.
3. Использовать UI-паттерны из `design_system/ui_kits/app` и `design_system/ui_kits/landing` как базовые референсы.
4. Соблюдать content rules: sentence case, без emoji, без маркетингового hype-языка.
5. Запрещены визуальные отклонения: bluish-purple gradients, glassmorphism, heavy shadow styles, произвольные status-pills.
6. Для иконок использовать Lucide stroke-only (`currentColor`) по правилам дизайн-системы.
7. Любой фронтовый PR/слайс должен явно подтвердить соответствие `design_system` в описании изменений.
8. Для layout и user flow ориентируемся на North Star экран [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png) (левый workspace-nav, центральный run-workbench, правый intervention rail).

## Capability Board (Roadmap v3)

Статус ведем по каждой capability в четырех осях: `BE / FE / Demo / QA`.

1. `C1` Workspace & Project Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset & Metrics Studio
5. `C5` Optimizer Run Monitor
6. `C6` Report + Champion Export/Import

## Repository Map

- `auto_agent_optimizer_РєРѕРЅС†РµРїС†РёСЏ_Рё_С‚Р·.md` - РїРѕР»РЅРѕРµ РўР— Рё РєРѕРЅС†РµРїС†РёСЏ.
- `Roadmap.md` - РїР»Р°РЅ РїРѕ РёС‚РµСЂР°С†РёСЏРј, СЃР»Р°Р№СЃР°Рј, СЃС‚Р°С‚СѓСЃР°Рј.
- `System_Architecture_Overview.md` - С‚РµРєСѓС‰Р°СЏ С†РµР»РµРІР°СЏ Р°СЂС…РёС‚РµРєС‚СѓСЂР°.
- `docs/adr` - Р¶СѓСЂРЅР°Р» Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹С… СЂРµС€РµРЅРёР№.
- `design_system` - обязательная дизайн-система (бренд, токены, UI kits, handoff); frontend реализуется строго по ней.
- `docs/specs/Frontend_Architecture_v0.md` - целевая фронтенд-архитектура (`React/TypeScript`, capability unlock, UX North Star).
- `langgraph-document-ai-platform` - РІРЅРµС€РЅРёР№ framework-РёСЃС‚РѕС‡РЅРёРє РґР»СЏ РёР·СѓС‡РµРЅРёСЏ Рё РїРµСЂРµРёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ (read-only РІ СЂР°РјРєР°С… СЌС‚РѕРіРѕ РїСЂРѕРµРєС‚Р°).
- `optimizer/dsl` - DSL v0 schema, loader Рё CLI-РІР°Р»РёРґР°С†РёСЏ.
- `optimizer/graph_ir` - runtime-neutral Graph IR v0, РІР°Р»РёРґР°С‚РѕСЂС‹ Рё CLI.
- `optimizer/dsl/compiler.py` - РєРѕРјРїРёР»СЏС‚РѕСЂ DSL -> Graph IR Рё РѕС‚С‡РµС‚ РєРѕРјРїРёР»СЏС†РёРё.
- `optimizer/renderer/langgraph_dai` - runtime renderer Рё Р·Р°РїСѓСЃРє Graph IR workflow.
- `optimizer/codegen` - DSL/IR -> СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅС‹Р№ РєРѕРґ Р°РіРµРЅС‚Р° (package + runner).
- `optimizer/tracing` - node-level СЃРѕР±С‹С‚РёСЏ РёСЃРїРѕР»РЅРµРЅРёСЏ Рё СЃРІРѕРґРєР° trace РїРѕ run.
- `optimizer/evaluation` - golden dataset contract, loader, oracle runner Рё CLI-РІР°Р»РёРґР°С†РёСЏ/РїСЂРѕРіРѕРЅ.
- `optimizer/evaluation/profile_schema.py` - typed contract `Evaluation Profile v0`.
- `optimizer/evaluation/profile_runner.py` - profile orchestration с переключением `dsl_runtime`/`native_runtime`.
- `optimizer/evaluation/native_compatibility.py` - preflight compatibility report для `native_runtime` target.
- `optimizer/evaluation/run_profile.py` - CLI profile-driven оценки.
- `optimizer/metrics` - middle-РјРµС‚СЂРёРєРё Рё СЃР»СѓР¶РµР±РЅС‹Рµ Р°РіСЂРµРіР°С‚РѕСЂС‹ РґР»СЏ arena scoring.
- `optimizer/evidence` - РіРµРЅРµСЂР°С†РёСЏ Evidence Pack (`comparison` + `diagnostics` + explainable diff).
- `optimizer/champion` - export Champion Bundle (`diagnostic_map`, `winner_graph_ir`, `generated_agent`, `manifest`).
- `frontend` - app-v3-aligned React/TypeScript workbench, evolving toward product capabilities C1..C6 (workspace/chat/patterns/datasets/runs/champion).
- `optimizer/frontend/dev_server.py` - lightweight frontend dev server (serves `frontend/dist` build + capability API endpoints).
- `optimizer/workspace` - JSON-backed workspace/project registry store for C1 product capability.
- `components` - deterministic demo-РєРѕРјРїРѕРЅРµРЅС‚С‹ РґР»СЏ РїР°Р№РїР»Р°Р№РЅРѕРІ (РІРєР»СЋС‡Р°СЏ AI-pattern РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹).
- `validators` - python-РІР°Р»РёРґР°С‚РѕСЂС‹ demo-СЃС†РµРЅР°СЂРёРµРІ (РІРєР»СЋС‡Р°СЏ style output guard).
- `docs/specs/Evaluation_Profile_v0.md` - РєРѕРЅС†РµРїС‚ profile-driven РѕС†РµРЅРєРё (task-specific metrics + pluggable evaluators).
- `examples/profiles` - example evaluation profiles (`stylizer_profile_ci_v0`, `ocr_support_profile_ci_v0`).
- `scripts/smoke_run_evaluation_profile.ps1` - smoke-проверка profile-driven path.
- `scripts/smoke_run_evaluation_profile_native_preflight.ps1` - smoke-проверка preflight-блокировки несовместимого native profile.
- `docs/specs/Evidence_Pack_v0.md` - РєРѕРЅС‚СЂР°РєС‚ Р°СЂС‚РµС„Р°РєС‚РѕРІ evidence РґР»СЏ winner/challenger Р°РЅР°Р»РёР·Р°.
- `docs/specs/Champion_Export_Bundle_v0.md` - РєРѕРЅС‚СЂР°РєС‚ champion bundle v0.
- `docs/specs/Native_Langgraph_DAI_Export_v0.md` - standalone native export contract Р±РµР· runtime-зависимости от optimizer.
- `docs/specs/Post_Export_Evaluation_Loop_v0.md` - контракт непрерывной оценки native champion после экспорта.
- `examples/dsl` - СЌС‚Р°Р»РѕРЅРЅС‹Рµ YAML-СЃРїРµРєРё, РІРєР»СЋС‡Р°СЏ stylizer РєР°РЅРґРёРґР°С‚РѕРІ (`style_direct_llm`, `style_pattern_cleaner`, `style_hitl_reviewer`).
- `examples/graph_ir` - СЌС‚Р°Р»РѕРЅРЅС‹Рµ Graph IR JSON-СЃРїРµРєРё.
- `examples/datasets` - СЌС‚Р°Р»РѕРЅРЅС‹Рµ golden dataset JSONL РєРµР№СЃС‹ (РІРєР»СЋС‡Р°СЏ `golden_linkedin_stylizer_v1.jsonl`).
- `examples/resources/ai_style_patterns_ru_v1.json` - СЃРїСЂР°РІРѕС‡РЅРёРє РёР·РІРµСЃС‚РЅС‹С… AI-РїР°С‚С‚РµСЂРЅРѕРІ РґР»СЏ stylizer-РєРµР№СЃР°.
- `scripts/smoke_validate_dsl.ps1` - smoke-РїСЂРѕРІРµСЂРєР° РІСЃРµС… DSL-РїСЂРёРјРµСЂРѕРІ.
- `scripts/smoke_validate_graph_ir.ps1` - smoke-РїСЂРѕРІРµСЂРєР° РІСЃРµС… Graph IR-РїСЂРёРјРµСЂРѕРІ.
- `scripts/smoke_compile_dsl_to_ir.ps1` - smoke-РєРѕРјРїРёР»СЏС†РёСЏ DSL РІ IR.
- `scripts/smoke_run_runtime_demo.ps1` - smoke runtime-РґРµРјРѕ РёСЃРїРѕР»РЅРµРЅРёСЏ workflow.
- `scripts/smoke_generate_agent_code.ps1` - smoke-РґРµРјРѕ РіРµРЅРµСЂР°С†РёРё Рё Р·Р°РїСѓСЃРєР° РєРѕРґРѕРІРѕРіРѕ Р°РіРµРЅС‚Р°.
- `scripts/smoke_validate_dataset.ps1` - smoke-РІР°Р»РёРґР°С†РёСЏ golden dataset.
- `scripts/smoke_run_oracle.ps1` - smoke-РїСЂРѕРіРѕРЅ executable oracle runner.
- `scripts/smoke_export_champion_bundle.ps1` - smoke-РїСЂРѕРіРѕРЅ champion bundle export.
- `scripts/smoke_frontend_shell.ps1` - smoke-РїСЂРѕРіРѕРЅ capability frontend shell (`C1..C6`).


## I3.S3 Artifacts

- `optimizer/arena` - equal-budget tournament runner Рё CLI СЃСЂР°РІРЅРµРЅРёСЏ 2-3 Р°СЂС…РёС‚РµРєС‚СѓСЂ.
- `examples/arena/support_tournament_v0.yaml` - live-РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ С‚СѓСЂРЅРёСЂР° stylizer-РєРµР№СЃР°.
- `examples/arena/support_tournament_ci_v0.yaml` - СЃС‚Р°Р±РёР»СЊРЅР°СЏ CI-РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ stylizer-С‚СѓСЂРЅРёСЂР°.
- `examples/arena/support_tournament_decision_v0.yaml` - live decision-РїСЂРѕС„РёР»СЊ (8 кейсов, `hash_stable`) РґР»СЏ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹С… СЂРµС€РµРЅРёР№.
- `examples/arena/support_tournament_ci_decision_v0.yaml` - CI decision-РїСЂРѕС„РёР»СЊ (8 кейсов, `hash_stable`).
- `examples/arena/support_tournament_full_v0.yaml` - live full-budget РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ stylizer-С‚СѓСЂРЅРёСЂР°.
- `examples/arena/support_tournament_ci_full_v0.yaml` - CI full-budget РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ stylizer-С‚СѓСЂРЅРёСЂР°.
- `scripts/smoke_run_arena.ps1` - smoke-РїСЂРѕРіРѕРЅ CI stylizer С‚СѓСЂРЅРёСЂР°.
- `scripts/smoke_run_arena_decision.ps1` - smoke-РїСЂРѕРіРѕРЅ CI decision-РїСЂРѕС„РёР»СЏ stylizer-С‚СѓСЂРЅРёСЂР°.
- `scripts/smoke_run_arena_live_decision.ps1` - smoke-РїСЂРѕРіРѕРЅ live decision-РїСЂРѕС„РёР»СЏ stylizer-С‚СѓСЂРЅРёСЂР°.
- `scripts/smoke_generate_evidence_pack.ps1` - smoke-РіРµРЅРµСЂР°С†РёСЏ Evidence Pack РїРѕ CI arena РєРѕРЅС„РёРіСѓ.
- `docs/specs/Architecture_Arena_v0.md` - config-first РєРѕРЅС‚СЂР°РєС‚ `budget`/`ranking`/`evaluator` РїРѕР»РёС‚РёРє С‚СѓСЂРЅРёСЂР°.

## I4.S1 Artifacts

- `optimizer/metrics/middle_metrics.py` - СЂР°СЃС‡РµС‚ middle-РјРµС‚СЂРёРє (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`).
- `optimizer/arena/tournament_schema.py` - СЂР°СЃС€РёСЂРµРЅРЅС‹Р№ РєРѕРЅС‚СЂР°РєС‚ `scoring` policy Рё ranking РїРѕ `composite_score`.
- `optimizer/arena/runner.py` - СЂР°СЃС‡РµС‚ `middle_metrics`, `composite_score` Рё `score_breakdown` РІ tournament output.
- `examples/arena/support_tournament_v0.yaml` - РґРµРјРѕ-РєРѕРЅС„РёРі СЃ РІРєР»СЋС‡РµРЅРЅС‹Рј `scoring`.
- `examples/arena/support_tournament_full_v0.yaml` - full-budget РґРµРјРѕ-РєРѕРЅС„РёРі СЃ РІРєР»СЋС‡РµРЅРЅС‹Рј `scoring`.

## I4.S2 Artifacts

- `optimizer/evidence/pack_builder.py` - СЃР±РѕСЂРєР° Evidence Pack payload Рё explainable winner/challenger diff.
- `optimizer/evidence/generate_pack.py` - CLI РіРµРЅРµСЂР°С†РёРё `evidence_pack.json` + `evidence_pack.md`.
- `docs/specs/Evidence_Pack_v0.md` - РєРѕРЅС‚СЂР°РєС‚ СЃС‚СЂСѓРєС‚СѓСЂС‹ evidence pack РґР»СЏ MVP v0.
- `scripts/smoke_generate_evidence_pack.ps1` - smoke-РїСЂРѕРіРѕРЅ РіРµРЅРµСЂР°С†РёРё evidence pack.

## I4.S3 Artifacts

- `optimizer/champion/diagnostic_map.py` - builder РїСЂРёРѕСЂРёС‚РёР·РёСЂРѕРІР°РЅРЅРѕР№ diagnostic map РґР»СЏ winner.
- `optimizer/champion/export_bundle.py` - CLI СЌРєСЃРїРѕСЂС‚Р° champion bundle РёР· arena СЂРµР·СѓР»СЊС‚Р°С‚Р°.
- `docs/specs/Champion_Export_Bundle_v0.md` - РєРѕРЅС‚СЂР°РєС‚ bundle Р°СЂС‚РµС„Р°РєС‚РѕРІ Рё СЃС‚СЂСѓРєС‚СѓСЂР° РєР°С‚Р°Р»РѕРіР°.
- `scripts/smoke_export_champion_bundle.ps1` - smoke-РїСЂРѕРІРµСЂРєР° champion bundle export.

## I4.S4 Direction (Done)

- native export target `langgraph_dai_native` (standalone runtime artifact).
- parity contract `DSL path vs native exported path`.
- champion bundle default switch to native runtime artifact.

## I4.S5 Artifacts

- `optimizer/champion/native_export.py` - minimal standalone native exporter на `framework`/`infra.openrouter`.
- `optimizer/champion/export_bundle.py` - bundle теперь включает `native_agent` и `native_runtime_smoke` проверку.
- `tests/unit/test_native_export.py` - unit-проверки native exporter.

## Dual Metrics Model

Р’ РїСЂРѕРµРєС‚Рµ Р·Р°РєСЂРµРїР»РµРЅР° РјРѕРґРµР»СЊ РґРІСѓС… С‚РёРїРѕРІ РјРµС‚СЂРёРє:

1. `Comparative Metrics` - С‚РѕР»СЊРєРѕ РґР»СЏ СЃСЂР°РІРЅРµРЅРёСЏ Р°СЂС…РёС‚РµРєС‚СѓСЂ Рё ranking.
2. `Diagnostic Signals` - С‚РѕР»СЊРєРѕ РґР»СЏ Р»РѕРєР°Р»РёР·Р°С†РёРё bottleneck Рё РїР»Р°РЅРёСЂРѕРІР°РЅРёСЏ intervention.

Р¤РёРєСЃР°С†РёСЏ СЂРµС€РµРЅРёСЏ: `ADR-0016`.

## Configurable Evaluation Model

РћС†РµРЅРєР° РІ РїР»Р°С‚С„РѕСЂРјРµ СЂР°Р·РІРёРІР°РµС‚СЃСЏ РєР°Рє `profile-driven` СЃР»РѕР№:

1. РњРµС‚СЂРёРєРё comparative/diagnostic Р·Р°РґР°СЋС‚СЃСЏ РїРѕРґ РєРѕРЅРєСЂРµС‚РЅС‹Р№ task type.
2. РњРµС‚РѕРґС‹ РѕС†РµРЅРєРё РїРѕРґРєР»СЋС‡Р°СЋС‚СЃСЏ РєР°Рє adapters (`golden_oracle`, `llm_judge`, `executable`, `render`, ...).
3. РР·РјРµРЅРµРЅРёРµ РїСЂРѕС„РёР»СЏ РјРµС‚СЂРёРє СЂР°СЃСЃРјР°С‚СЂРёРІР°РµС‚СЃСЏ РєР°Рє agent workflow СЃ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Рј HITL approve.

РўРµРєСѓС‰Р°СЏ СЃРїРµС†РёС„РёРєР°С†РёСЏ РЅР°РїСЂР°РІР»РµРЅРёСЏ:

- [Evaluation_Profile_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Evaluation_Profile_v0.md)

## Definition of Done For a Slice

1. Р РµР°Р»РёР·Р°С†РёСЏ Р·Р°РІРµСЂС€РµРЅР° Рё РїСЂРѕРІРµСЂРµРЅР° Р»РѕРєР°Р»СЊРЅРѕ.
2. Новый backend-инкремент доступен для проверки через frontend в том же слайсе.
3. Обновлен demo-сценарий с наблюдаемым результатом по новому пути.
4. Для фронтовых изменений подтверждено соответствие `design_system` (tokens + typography + components + voice).
5. РћР±РЅРѕРІР»РµРЅС‹ `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` (РµСЃР»Рё Р·Р°С‚СЂРѕРЅСѓС‚Рѕ).
6. Р”РѕР±Р°РІР»РµРЅ/РѕР±РЅРѕРІР»РµРЅ ADR РїСЂРё Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹С… РёР·РјРµРЅРµРЅРёСЏС….
7. РЎРґРµР»Р°РЅ РѕС‚РґРµР»СЊРЅС‹Р№ git commit СЃ РїСЂРёРІСЏР·РєРѕР№ Рє СЃР»Р°Р№СЃСѓ (РЅР°РїСЂРёРјРµСЂ `I1.S2`).
8. Р’С‹РїРѕР»РЅРµРЅ С‚РµСЃС‚-РіРµР№С‚ СЃРѕРіР»Р°СЃРЅРѕ С‚РёРїСѓ СЃР»Р°Р№СЃР° (fast/targeted/full, СЃРј. `Test Policy`).

## Test Policy

РЎС‚СЂСѓРєС‚СѓСЂР° С‚РµСЃС‚РѕРІ:

1. `tests/unit`
2. `tests/integration`
3. `tests/e2e`

РњРѕРґРµР»СЊ РіРµР№С‚РѕРІ (РїРѕ РєР»Р°СЃСЃСѓ РёР·РјРµРЅРµРЅРёР№):

1. `Fast gate` (`FE-only` микроизменения без изменения API контракта):
   - `python -m pytest tests/unit/test_frontend_contracts.py`,
   - `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`.
2. `Targeted gate` (`FE + API slice` или локальное backend-изменение):
   - все из `Fast gate`,
   - `python -m pytest tests/integration/test_frontend_dev_server.py`,
   - профильные e2e/интеграции для затронутого пути.
3. `Full gate` (РєСЂСѓРїРЅС‹Р№ СЃР»Р°Р№СЃ, release-candidate, РёР·РјРµРЅРµРЅРёСЏ evaluation/runtime/champion paths):
   - РІСЃРµ РёР· `Targeted gate`,
   - РїРѕР»РЅС‹Р№ `python -m pytest`.

РџРѕР»РЅС‹Р№ РїСЂРѕРіРѕРЅ (РґР»СЏ `Full gate`):

```powershell
python -m pytest
```

РџСЂРѕРіРѕРЅ РїРѕ СѓСЂРѕРІРЅСЏРј:

```powershell
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m e2e
```

Frontend-only команды:

```powershell
python -m pytest tests/unit/test_frontend_contracts.py
python -m pytest tests/e2e/test_frontend_shell_smoke_script.py
```

Р’Р°Р¶РЅРѕ РґР»СЏ Р»РѕРєР°Р»СЊРЅРѕР№ РїСЂРѕРІРµСЂРєРё UI/API:

1. РїРѕСЃР»Рµ РёР·РјРµРЅРµРЅРёР№ backend-РЅРґРїРѕРёРЅС‚РѕРІ РїРµСЂРµР·Р°РїСѓСЃРєР°Р№С‚Рµ dev server;
2. РїСЂРѕРІРµСЂСЏР№С‚Рµ, С‡С‚Рѕ frontend proxy СЃРјРѕС‚СЂРёС‚ РЅР° Р°РєС‚СѓР°Р»СЊРЅС‹Р№ backend instance, РёРЅР°С‡Рµ РІРѕР·РјРѕР¶РЅС‹ `404` РЅР° `/api/*`.

Live runtime-С‚РµСЃС‚С‹ (РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ, РЅРµР±Р»РѕРєРёСЂСѓСЋС‰РёРµ):

```powershell
$env:RUN_LIVE_ARENA="1"
python -m pytest -m live
```

## PowerShell JSON Tip

Р”Р»СЏ CLI-РєРѕРјР°РЅРґ, РіРґРµ РїРµСЂРµРґР°РµС‚СЃСЏ JSON payload, РІ PowerShell РёСЃРїРѕР»СЊР·СѓР№С‚Рµ `--payload-file` РєР°Рє РѕСЃРЅРѕРІРЅРѕР№ СЃРїРѕСЃРѕР± Р·Р°РїСѓСЃРєР°.
Р­С‚Рѕ РёСЃРєР»СЋС‡Р°РµС‚ РѕС€РёР±РєРё СЌРєСЂР°РЅРёСЂРѕРІР°РЅРёСЏ РІРёРґР° `unrecognized arguments`.

## Runtime Demo Quickstart (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path .\tmp | Out-Null
'{"draft_post":"Р’ СЃРѕРІСЂРµРјРµРЅРЅРѕРј РјРёСЂРµ РЅРµР»СЊР·СЏ РЅРµРґРѕРѕС†РµРЅРёРІР°С‚СЊ СЂРѕР»СЊ СЂРµРґР°РєС‚СѓСЂС‹. Р”Р°РІР°Р№С‚Рµ СЂР°Р·Р±РµСЂРµРјСЃСЏ, РєР°Рє РїРµСЂРµРїРёСЃР°С‚СЊ РїРѕСЃС‚ Р¶РёРІРµРµ Рё СЃРѕС…СЂР°РЅРёС‚СЊ С„Р°РєС‚С‹."}' | Set-Content -LiteralPath .\tmp\runtime_payload.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\style_direct_llm.yaml --payload-file .\tmp\runtime_payload.json --pretty
```

РџРѕР»РЅС‹Р№ smoke-РїСЂРѕРіРѕРЅ РґРµРјРѕ:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
```

## Oracle Demo Quickstart (PowerShell)

Р‘С‹СЃС‚СЂР°СЏ РїСЂРѕРІРµСЂРєР° РёСЃРїРѕР»РЅСЏРµРјРѕР№ РѕС†РµРЅРєРё РЅР° golden dataset (РґРµС‚РµСЂРјРёРЅРёСЂРѕРІР°РЅРЅС‹Р№ СЂРµР¶РёРј РґР»СЏ smoke/CI):

```powershell
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\style_direct_llm.yaml --dataset-file .\examples\datasets\golden_linkedin_stylizer_v1.jsonl --execution-mode expected_stub --pretty
```

РџРѕР»РЅС‹Р№ smoke-РїСЂРѕРіРѕРЅ oracle:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_oracle.ps1
```


## Arena Demo Quickstart (PowerShell)

РЎС‚Р°Р±РёР»СЊРЅС‹Р№ CI-С‚СѓСЂРЅРёСЂ (deterministic `expected_stub`):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty
```

Р’ СѓСЃРїРµС€РЅРѕРј РІС‹РІРѕРґРµ РїСЂРѕРІРµСЂСЊС‚Рµ:

1. `scoring_enabled: true`
2. `ranking_policy[0].name: composite_score`
3. Сѓ РєР°Р¶РґРѕРіРѕ СѓС‡Р°СЃС‚РЅРёРєР° РµСЃС‚СЊ `middle_metrics`, `composite_score`, `score_breakdown`
4. РµСЃС‚СЊ СЃРµРєС†РёРё `comparison` Рё `diagnostics`
5. РІ `diagnostics.participants[].signals` РµСЃС‚СЊ `top_bottlenecks` Рё `intervention_hints`

Live runtime-РґРµРјРѕ (winner РјРѕР¶РµС‚ РјРµРЅСЏС‚СЊСЃСЏ РёР·-Р·Р° LLM):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
```

Decision CI-турнир (deterministic, бюджет 8 кейсов, `hash_stable`):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --pretty
```

Decision LIVE-турнир (бюджет 8 кейсов, профиль для принятия решений):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_decision_v0.yaml --pretty
```

CI full-budget турнир (весь dataset):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_full_v0.yaml --pretty
```

Live runtime full-budget турнир (весь dataset, дороже и дольше):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_full_v0.yaml --pretty
```

РџРѕР»РЅС‹Р№ smoke-РїСЂРѕРіРѕРЅ arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live smoke-РїСЂРѕРіРѕРЅ arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Decision smoke-прогон arena (CI):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_decision.ps1
```

Decision live smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_decision.ps1
```

Full smoke-прогон arena (CI full):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_full.ps1
```

Live full smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_full.ps1
```

## Evaluation Profile Quickstart (PowerShell)

DSL target:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
```

Native target:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
```

Важно (текущий статус на 2026-05-21):

1. canonical `stylizer_profile_ci_v0` успешно запускается на `native_runtime` (DSL->Native parity для demo-critical пути достигнут в `I4.S6a`).
2. preflight сохраняется как fail-fast guard для реально неразрешимых source/binding проблем (например broken graph source или unresolved callable).
3. workaround policy `skip_unsupported` отклонен; `I4.S8` закрыт, `V2.1.S3a` выполнен, следующий delivery-слайс — `V2.1.S3`.

Smoke-прогон profile-driven path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile_native_preflight.ps1
```

DSL-vs-native parity harness (структурный CI-gate):

```powershell
python -m optimizer.parity.run --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --cases-limit 1 --fail-on-mismatch --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_dsl_native_parity.ps1
```

## Evidence Pack Quickstart (PowerShell)

Генерация evidence pack напрямую из CI arena-конфига:

```powershell
python -m optimizer.evidence.generate_pack --arena-file .\examples\arena\support_tournament_ci_v0.yaml --out-dir .\tmp\evidence_pack --pretty
```

Генерация evidence pack из уже сохраненного arena JSON:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty | Out-File -LiteralPath .\tmp\arena_result.json -Encoding utf8
python -m optimizer.evidence.generate_pack --arena-result-file .\tmp\arena_result.json --out-dir .\tmp\evidence_pack --pretty
```

Smoke-прогон evidence pack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_evidence_pack.ps1
```

## Champion Bundle Quickstart (PowerShell)

Экспорт champion bundle напрямую из CI decision arena-конфига:

```powershell
python -m optimizer.champion.export_bundle --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
```

После запуска проверьте:

1. `bundle_manifest.json` (`default_runtime_target=native_runtime`, есть `default_entrypoint_file` и `legacy_debug_entrypoint_file`),
2. `parity_report.json` (`is_equivalent_agent=true` и `native_runtime_smoke.passed=true`),
3. `README.bundle.md` в каталоге bundle (native-first инструкция для разработчика),
4. `native_agent\app\run.py` (standalone runtime entrypoint без `optimizer.*` импортов).

Smoke-прогон champion bundle export:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_export_champion_bundle.ps1
```

## Frontend Shell Quickstart (PowerShell)

Собрать React/TS фронтенд (выполнять после изменений в `frontend/src`):

```powershell
cd .\frontend
npm install
npm run build
cd ..
```

Запуск capability shell (`C1..C6`):

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

Открыть в браузере:

```text
http://127.0.0.1:4173/
```

Раздельный запуск frontend и backend:

1. Backend (терминал 1):

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

2. Frontend Vite dev server (терминал 2):

```powershell
cd .\frontend
npm run dev
```

3. Открыть frontend:

```text
http://127.0.0.1:5173/
```

Как работает `/api` в раздельном режиме:

1. Фронт на `5173` обращается к относительным URL вида `/api/...`.
2. Vite proxy перенаправляет эти запросы на Python backend `http://127.0.0.1:4173`.
3. Также через proxy идет `/design_system/*`, поэтому токены и ассеты дизайн-системы корректно доступны в dev.

Smoke-прогон frontend shell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_frontend_shell.ps1
```

Resume quickstart:

```powershell
'{"query":"Create safe ticket","action_risk":"low"}' | Set-Content -LiteralPath .\tmp\start.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --payload-file .\tmp\start.json --task-id demo-resume-task --checkpoint-dir .\tmp\runtime_checkpoints --pretty

'{"action_risk":"high","review_decision":"approve"}' | Set-Content -LiteralPath .\tmp\resume.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --resume-task-id demo-resume-task --payload-file .\tmp\resume.json --checkpoint-dir .\tmp\runtime_checkpoints --pretty
```

## OpenRouter Setup (For Real LLM Calls)

РљРѕРіРґР° РїРµСЂРµР№РґРµРј Рє runtime-СЃР»Р°Р№СЃР°Рј (`I2.*`), РјРѕР¶РЅРѕ РІРєР»СЋС‡РёС‚СЊ СЂРµР°Р»СЊРЅС‹Рµ РІС‹Р·РѕРІС‹ LLM.

1. РЎРєРѕРїРёСЂСѓР№С‚Рµ `.env.example` РІ `.env`.
2. Р—Р°РїРѕР»РЅРёС‚Рµ `OPENROUTER_API_KEY`.
3. Для экономичного demo-цикла используйте более дешевую модель в `OPENROUTER_MODEL` (по умолчанию в `.env.example` задана `meta-llama/llama-3.1-8b-instruct`).
4. Для более высокого качества на финальных full-прогонах можно временно переключаться на более сильную модель.

Р’Р°Р¶РЅРѕ: `.env` РґРѕР±Р°РІР»РµРЅ РІ `.gitignore` Рё РЅРµ РґРѕР»Р¶РµРЅ РїРѕРїР°РґР°С‚СЊ РІ git.





