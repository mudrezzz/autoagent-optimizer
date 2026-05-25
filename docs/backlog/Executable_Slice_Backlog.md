# Executable Slice Backlog

## Purpose

Р­С‚РѕС‚ РґРѕРєСѓРјРµРЅС‚ РїРµСЂРµРІРѕРґРёС‚ РўР— РІ РёСЃРїРѕР»РЅРёРјС‹Рµ СЃР»Р°Р№СЃС‹ СЃ СЏРІРЅС‹РјРё РєСЂРёС‚РµСЂРёСЏРјРё РїСЂРёРµРјРєРё, Р·Р°РІРёСЃРёРјРѕСЃС‚СЏРјРё Рё РїРѕСЂСЏРґРєРѕРј СЂРµР°Р»РёР·Р°С†РёРё.

## Prioritization Policy

1. РЎРЅР°С‡Р°Р»Р° Р·Р°РєСЂС‹РІР°РµРј СЃРєРІРѕР·РЅРѕР№ РїСѓС‚СЊ MVP-1 (`DSL -> IR -> Render -> Run -> Evaluate -> Evidence`).
2. РџСЂРёРѕСЂРёС‚РµС‚ Сѓ СЃР»Р°Р№СЃРѕРІ, РєРѕС‚РѕСЂС‹Рµ:
   - СЃРЅРёР¶Р°СЋС‚ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Р№ СЂРёСЃРє;
   - РґР°СЋС‚ РїСЂРѕРІРµСЂСЏРµРјС‹Р№ end-to-end РїСЂРѕРіСЂРµСЃСЃ;
   - СЂР°Р·Р±Р»РѕРєРёСЂСѓСЋС‚ РЅРµСЃРєРѕР»СЊРєРѕ СЃР»РµРґСѓСЋС‰РёС… СЃР»Р°Р№СЃРѕРІ.
3. Р’ РєР°Р¶РґРѕРј Р°РєС‚РёРІРЅРѕРј РѕРєРЅРµ РґРµС‚Р°Р»СЊРЅРѕ РїР»Р°РЅРёСЂСѓСЋС‚СЃСЏ С‚РѕР»СЊРєРѕ Р±Р»РёР¶Р°Р№С€РёРµ 1-2 РёС‚РµСЂР°С†РёРё.

## Active Window (Now)

- `Current Focus`: MVP-2 product realignment vertical delivery (`Roadmap v3`)
- `Active Next Slice`: V2.3.S5

## Active Capability Board

Статус фиксируется по осям `BE / FE / Demo / QA`.

Дополнительный обязательный gate для всех `FE` статусов: соответствие `design_system`.

1. `C1` Workspace & Project Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset & Metrics Studio
5. `C5` Optimizer Run Monitor
6. `C6` Report + Champion Export/Import

## Near-Term Vertical Iterations (V2)

### V2.1 - Legacy Capability Shell Foundation

- Status: In Progress
- Goal: сохранить уже сделанный legacy capability shell как технический фундамент.
- Design constraint: каждый UI-инкремент реализуется на токенах и паттернах `design_system`.
- Slices:
  1. `V2.1.S1` legacy shell + API skeleton. (`Done`)
  2. `V2.1.S2` legacy DSL validate/compile slice. (`Done`)
  3. `V2.1.S3` legacy run/trace slice.
  4. `V2.1.S4` legacy arena ranking slice.
  5. `V2.1.S5` legacy bundle inspector slice.

- Progress (2026-05-22):
  1. Добавлен `frontend/` capability shell с вкладками C1..C6 и состояниями `idle/loading/success/error`.
  2. Добавлен lightweight backend endpoint `POST /api/c1/validate-compile` (реальный DSL validate+compile path).
  3. Добавлены stub-endpoints `GET /api/c2..c6/sample` для сквозной UI-проверки.
  4. Добавлены unit/integration/e2e проверки frontend shell + smoke-скрипт `scripts/smoke_frontend_shell.ps1`.

### V2.2 - Evaluation Fabric Expansion

- Status: In Progress
- Goal: расширить configurable evaluation fabric и связать ее с UI без ухода в ad-hoc.
- Design constraint: расширения UI допускаются только в рамках `design_system` visual/content rules.
- Slices:
  1. `V2.2.S1` evaluator adapters (`golden`/`llm_judge`/`executable`/`render`).
  2. `V2.2.S2` comparative/diagnostic UI panels.
  3. `V2.2.S3` export/import loop entry points.
  4. `V2.2.S4` unified budget presets (`smoke/decision/full`) across run surfaces.
  5. `V2.2.S5` one-click end-to-end demo scenario with saved artifacts.

### V2.3 - Product Realignment Vertical Slices (Primary)

- Status: Planned
- Goal: выстроить пользовательский flow по ТЗ (workspace -> chat -> candidates -> dataset/metrics -> run -> report -> champion -> import loop).
- Design constraint: каждый слайс обязателен как `BE + FE + Demo + QA` и проверяется в UI.
- Slices:
  1. `V2.3.S1` C1 workspace/project registry. (`Done`)
  2. `V2.3.S1a` SaaS IA split (Projects Hub vs Project Workspace). (`Done`)
  3. `V2.3.S2` C2 project chat brief-to-candidates v0. (`Done`)
  4. `V2.3.S3` C3 pattern library + RAG include/exclude controls. (`Done`)
  5. `V2.3.S4` candidate assembly + internal compile readiness gate. (`Done`)
  6. `V2.3.S5` C4 dataset studio v0.
  7. `V2.3.S6` C4 metrics/evaluators studio v0.
  8. `V2.3.S7` C5 optimizer setup + budget/epoch controls.
  9. `V2.3.S8` C5 run monitor + version manifest timeline.
  10. `V2.3.S9` C6 report + champion export/import loop.

---

## Detailed Backlog: I1-I2

### I1.S1 - DSL v0 schema draft (YAML-first)

- Status: Done
- Goal: Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ РјРёРЅРёРјР°Р»СЊРЅС‹Р№ СЏР·С‹Рє РѕРїРёСЃР°РЅРёСЏ РїСЂРѕРµРєС‚Р°/Р°СЂС…РёС‚РµРєС‚СѓСЂС‹ РґР»СЏ РґР°Р»СЊРЅРµР№С€РµР№ РєРѕРјРїРёР»СЏС†РёРё.
- Inputs: FR-4, FR-1/2/3 РёР· РўР—.
- Deliverables:
  - `optimizer/dsl/schema.py` (typed contracts),
  - `examples/dsl/*.yaml`,
  - `docs/specs/DSL_v0.md`.
- Acceptance Criteria:
  1. Р’Р°Р»РёРґРёСЂСѓРµС‚СЃСЏ РјРёРЅРёРјСѓРј 3 СЃС†РµРЅР°СЂРёСЏ: `direct_llm`, `ocr_first`, `hitl_gate`.
  2. РћС€РёР±РєРё РІР°Р»РёРґР°С†РёРё С‡РµР»РѕРІРµРєРѕС‡РёС‚Р°РµРјС‹Рµ Рё СѓРєР°Р·С‹РІР°СЋС‚ РїСѓС‚СЊ РґРѕ РїРѕР»СЏ.
  3. Р•СЃС‚СЊ smoke-check РєРѕРјР°РЅРґР° РґР»СЏ DSL validation.
- Dependencies: none.
- Risks: РїРµСЂРµСѓСЃР»РѕР¶РЅРµРЅРёРµ DSL РґРѕ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ Р±Р°Р·РѕРІРѕРіРѕ СЂРµРЅРґРµСЂР°.

### I1.S2 - Graph IR v0 typed model

- Status: Done
- Goal: runtime-neutral РїСЂРµРґСЃС‚Р°РІР»РµРЅРёРµ РіСЂР°С„Р°, РЅРµР·Р°РІРёСЃРёРјРѕРµ РѕС‚ РєРѕРЅРєСЂРµС‚РЅРѕРіРѕ runtime.
- Inputs: FR-5, FR-6.
- Deliverables:
  - `optimizer/graph_ir/models.py`,
  - `optimizer/graph_ir/validators.py`,
  - `docs/specs/GraphIR_v0.md`.
- Acceptance Criteria:
  1. IR РїРѕРєСЂС‹РІР°РµС‚ node types: `llm`, `deterministic`, `tool`, `validator`, `hitl_gate`.
  2. Р•СЃС‚СЊ edge-РІР°Р»РёРґР°С†РёСЏ, РІРєР»СЋС‡Р°СЏ start/end Рё unreachable nodes.
  3. Р•СЃС‚СЊ СЃРµСЂРёР°Р»РёР·Р°С†РёСЏ/РґРµСЃРµСЂРёР°Р»РёР·Р°С†РёСЏ Р±РµР· РїРѕС‚РµСЂРё СЃС‚СЂСѓРєС‚СѓСЂС‹.
- Dependencies: I1.S1.
- Risks: РїСЂРѕС‚РµРєР°РЅРёРµ runtime-СЃРїРµС†РёС„РёС‡РЅС‹С… РїРѕР»РµР№ РІ IR.

### I1.S3 - DSL -> IR compiler v0

- Status: Done
- Goal: РєРѕРјРїРёР»СЏС†РёСЏ DSL РІ Graph IR СЃ РѕС‚С‡РµС‚РѕРј Рѕ С‚СЂР°РЅСЃС„РѕСЂРјР°С†РёРё.
- Inputs: FR-4, FR-5.
- Deliverables:
  - `optimizer/dsl/compiler.py`,
  - `optimizer/dsl/compile_report.py`.
- Acceptance Criteria:
  1. Р›СЋР±РѕР№ РІР°Р»РёРґРЅС‹Р№ DSL РёР· examples РєРѕРјРїРёР»РёСЂСѓРµС‚СЃСЏ РІ РІР°Р»РёРґРЅС‹Р№ IR.
  2. РћС‚С‡РµС‚ РєРѕРјРїРёР»СЏС†РёРё СЃРѕРґРµСЂР¶РёС‚ warnings/errors Рё node mapping.
  3. Р•СЃС‚СЊ regression tests РЅР° compile success/failure.
- Dependencies: I1.S1, I1.S2.
- Risks: РЅРµСЏРІРЅР°СЏ РјР°РіРёСЏ РІ compiler; СЂРµС€Р°РµС‚СЃСЏ explicit mapping rules.

### I2.S1 - LangGraph renderer adapter on top of langgraph-dai

- Status: Done
- Goal: РїСЂРµРІСЂР°С‚РёС‚СЊ IR РІ РёСЃРїРѕР»РЅСЏРµРјС‹Р№ workflow С‡РµСЂРµР· `BaseWorkflow`.
- Inputs: FR-6, ADR-0001.
- Deliverables:
  - `optimizer/renderer/langgraph_dai/adapter.py`,
  - `optimizer/renderer/langgraph_dai/workflow_builder.py`,
  - renderer smoke script.
- Acceptance Criteria:
  1. IR СЂРµРЅРґРµСЂРёС‚СЃСЏ РІ workflow Рё РІС‹РїРѕР»РЅСЏРµС‚СЃСЏ `invoke`.
  2. РџРѕРґРґРµСЂР¶РёРІР°РµС‚СЃСЏ РјРёРЅРёРјСѓРј linear flow + one conditional branch.
  3. Adapter РёР·РѕР»РёСЂСѓРµС‚ РІРЅРµС€РЅСЋСЋ Р±РёР±Р»РёРѕС‚РµРєСѓ РІ РѕС‚РґРµР»СЊРЅРѕРј РјРѕРґСѓР»Рµ.
- Dependencies: I1.S2, I1.S3.
- Risks: Р·Р°РІРёСЃРёРјРѕСЃС‚СЊ РѕС‚ internal API РІРЅРµС€РЅРµР№ Р±РёР±Р»РёРѕС‚РµРєРё.

### I2.S2 - Agent code generation v0

- Status: Done
- Goal: РїРѕР»СѓС‡РёС‚СЊ materialized Python-Р°СЂС‚РµС„Р°РєС‚ Р°РіРµРЅС‚Р° РёР· Р»СѓС‡С€РµР№ DSL/IR РєРѕРЅС„РёРіСѓСЂР°С†РёРё.
- Inputs: FR-6, runtime path I2.S1.
- Deliverables:
  - `optimizer/codegen/agent_generator.py`,
  - `optimizer/codegen/generate.py`,
  - `docs/specs/Agent_Codegen_v0.md`.
- Acceptance Criteria:
  1. Р•СЃС‚СЊ CLI РіРµРЅРµСЂР°С†РёРё РёР· DSL РёР»Рё Graph IR.
  2. Р“РµРЅРµСЂР°С‚РѕСЂ СЃРѕР·РґР°РµС‚ runnable package + runner script.
  3. Р•СЃС‚СЊ smoke-РїСѓС‚СЊ `DSL -> generate code -> run generated agent`.
- Dependencies: I1.S3, I2.S1.
- Risks: fallback-Р»РѕРіРёРєР° РјРѕР¶РµС‚ СЃРєСЂС‹С‚СЊ РѕС‚СЃСѓС‚СЃС‚РІРёРµ production-РѕР±СЂР°Р±РѕС‚С‡РёРєРѕРІ, РїРѕСЌС‚РѕРјСѓ РЅСѓР¶РЅС‹ СЏРІРЅС‹Рµ TODO РІ Р°СЂС‚РµС„Р°РєС‚Рµ.

### I2.S3 - Node event capture + white-box trace v0

- Status: Done
- Goal: СЃРЅСЏС‚СЊ node-level СЃРѕР±С‹С‚РёСЏ Рё СЃРґРµР»Р°С‚СЊ Р±Р°Р·РѕРІС‹Р№ trace storage format.
- Inputs: FR-9, FR-10.
- Deliverables:
  - `optimizer/tracing/node_events.py`,
  - `optimizer/tracing/trace_store.py`,
  - `docs/specs/Whitebox_Trace_v0.md`.
- Acceptance Criteria:
  1. Р”Р»СЏ РєР°Р¶РґРѕРіРѕ node С„РёРєСЃРёСЂСѓСЋС‚СЃСЏ `started/completed/failed`.
  2. Trace РїСЂРёРІСЏР·Р°РЅ Рє run_id/task_id.
  3. РњРѕР¶РЅРѕ РїРѕР»СѓС‡РёС‚СЊ summary РїРѕ run (node count, failures, duration).
- Dependencies: I2.S1.
- Risks: СЂР°Р·СЂС‹РІ РјРµР¶РґСѓ runtime events Рё evaluation metrics.

### I2.S4 - Resume/checkpoint contract path

- Status: Done
- Goal: РїРѕРґС‚РІРµСЂР¶РґРµРЅРЅС‹Р№ invoke/resume СЃС†РµРЅР°СЂРёР№ РґР»СЏ РґРѕР»РіРёС… execution.
- Inputs: FR-6, FR-19.
- Deliverables:
  - resume state contract tests,
  - checkpoint integration smoke.
- Acceptance Criteria:
  1. interrupt/resume РїСЂРѕС…РѕРґРёС‚ Р±РµР· РїРѕС‚РµСЂРё state.
  2. task/thread id РєРѕРЅСЃРёСЃС‚РµРЅС‚РЅРѕ РїРµСЂРµРЅРѕСЃРёС‚СЃСЏ РІ runtime.
  3. Р•СЃС‚СЊ negative tests РґР»СЏ missing/invalid task_id.
- Dependencies: I2.S1.
- Risks: РЅРµРєРѕРЅСЃРёСЃС‚РµРЅС‚РЅРѕСЃС‚СЊ state-РјРѕРґРµР»Рё РјРµР¶РґСѓ invoke Рё resume.

---

## Detailed Backlog: I3-I4

### I3.S1 - Golden dataset JSONL + loader

- Status: Done
- Goal: Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ РµРґРёРЅС‹Р№ dataset-РєРѕРЅС‚СЂР°РєС‚ Рё Р·Р°РіСЂСѓР·С‡РёРє РґР»СЏ evaluation-РёС‚РµСЂР°С†РёР№.
- Inputs: FR-7, FR-8 (РїРѕРґРіРѕС‚РѕРІРєР° Рє oracle/arena).
- Deliverables:
  - `optimizer/evaluation/dataset_schema.py`,
  - `optimizer/evaluation/dataset_loader.py`,
  - `optimizer/evaluation/validate_dataset.py`,
  - `examples/datasets/golden_support_v1.jsonl`.
- Acceptance Criteria:
  1. Р’Р°Р»РёРґРЅС‹Р№ JSONL РґР°С‚Р°СЃРµС‚ Р·Р°РіСЂСѓР¶Р°РµС‚СЃСЏ Р±РµР· РѕС€РёР±РѕРє.
  2. РќРµРІР°Р»РёРґРЅС‹Рµ СЃС‚СЂРѕРєРё РґР°СЋС‚ РїРѕРЅСЏС‚РЅСѓСЋ РѕС€РёР±РєСѓ СЃ РЅРѕРјРµСЂРѕРј СЃС‚СЂРѕРєРё.
  3. CLI РІР°Р»РёРґР°С†РёРё РІРѕР·РІСЂР°С‰Р°РµС‚ summary Рё РєРѕСЂСЂРµРєС‚РЅС‹Р№ exit code.
- Dependencies: I2.S4.
- Risks: РЅРµРґРѕРѕРїСЂРµРґРµР»РµРЅРЅС‹Р№ `expected` РєРѕРЅС‚СЂР°РєС‚ РґР»СЏ СЃР»РѕР¶РЅС‹С… РґРѕРјРµРЅРЅС‹С… Р·Р°РґР°С‡ (Р±СѓРґРµС‚ СѓС‚РѕС‡РЅРµРЅ РІ I3.S2).

### I3.S2 - Executable oracle runner (schema/pytest)

- Status: Done
- Goal: РёСЃРїРѕР»РЅСЏРµРјР°СЏ oracle-РїСЂРѕРІРµСЂРєР° СЂРµР·СѓР»СЊС‚Р°С‚Р° РїРѕ `expected` РєРѕРЅС‚СЂР°РєС‚Сѓ РґР°С‚Р°СЃРµС‚Р°.
- Deliverables:
  - `optimizer/evaluation/oracle_rules.py`,
  - `optimizer/evaluation/oracle_runner.py`,
  - `optimizer/evaluation/run_oracle.py`,
  - `scripts/smoke_run_oracle.ps1`,
  - `docs/specs/Oracle_Runner_v0.md`.
- Acceptance Criteria:
  1. Р•СЃС‚СЊ rule-contract v0 (`must_include`/`forbidden`) Рё pass/fail РїРѕ РєР°Р¶РґРѕРјСѓ РєРµР№СЃСѓ.
  2. CLI РІС‹РґР°РµС‚ summary (`cases_total/passed/failed/pass_rate`) Рё РєРѕСЂСЂРµРєС‚РЅС‹Р№ exit code.
  3. Р•СЃС‚СЊ deterministic `expected_stub` СЂРµР¶РёРј РґР»СЏ smoke/CI.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё Р·РµР»РµРЅС‹Р№ РїРѕР»РЅС‹Р№ `python -m pytest`.
- Dependencies: I3.S1.
- Risks: РїСЂР°РІРёР»Р° v0 С‚РµРєСЃС‚РѕРІС‹Рµ Рё РЅРµ РїРѕРєСЂС‹РІР°СЋС‚ СЃРµРјР°РЅС‚РёС‡РµСЃРєСѓСЋ СЌРєРІРёРІР°Р»РµРЅС‚РЅРѕСЃС‚СЊ РѕС‚РІРµС‚РѕРІ.

### I3.S3 - Architecture Arena equal-budget tournament v0

- Status: Done
- Goal: СЃСЂР°РІРЅРµРЅРёРµ 2-3 Р°СЂС…РёС‚РµРєС‚СѓСЂ РІ СЂР°РІРЅРѕРј Р±СЋРґР¶РµС‚Рµ СЃ reproducible РѕС‚С‡РµС‚РѕРј.
- Deliverables:
  - `optimizer/arena/tournament_schema.py`,
  - `optimizer/arena/io.py`,
  - `optimizer/arena/runner.py`,
  - `optimizer/arena/run_tournament.py`,
  - `examples/arena/support_tournament_v0.yaml`,
  - `scripts/smoke_run_arena.ps1`,
  - `docs/specs/Architecture_Arena_v0.md`.
- Acceptance Criteria:
  1. РћРґРёРЅ CLI-Р·Р°РїСѓСЃРє СЃСЂР°РІРЅРёРІР°РµС‚ РјРёРЅРёРјСѓРј 2 Рё РјР°РєСЃРёРјСѓРј 3 Р°СЂС…РёС‚РµРєС‚СѓСЂС‹ РЅР° РѕР±С‰РµРј РґР°С‚Р°СЃРµС‚Рµ.
  2. Equal-budget policy (`equal_cases`) РїСЂРёРјРµРЅСЏРµС‚ РѕРґРёРЅР°РєРѕРІС‹Р№ РЅР°Р±РѕСЂ РєРµР№СЃРѕРІ РґР»СЏ РІСЃРµС… СѓС‡Р°СЃС‚РЅРёРєРѕРІ.
  3. РћС‚С‡РµС‚ СЃРѕРґРµСЂР¶РёС‚ ranking Рё winner РїРѕ РїСЂРѕР·СЂР°С‡РЅС‹Рј РїСЂР°РІРёР»Р°Рј tie-break.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё Р·РµР»РµРЅС‹Р№ РїРѕР»РЅС‹Р№ `python -m pytest`.
- Dependencies: I3.S2.
- Risks: `expected_stub` СЂРµР¶РёРј РґР°РµС‚ СѓРїСЂРѕС‰РµРЅРЅС‹Р№ baseline Рё РЅРµ Р·Р°РјРµРЅСЏРµС‚ production runtime-СЃСЂР°РІРЅРµРЅРёРµ.

### I4.S1 - Middle-metrics v0

- Status: Done
- Goal: РІРІРµСЃС‚Рё РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Рµ РјРµС‚СЂРёРєРё РєР°С‡РµСЃС‚РІР°/СЃС‚РѕРёРјРѕСЃС‚Рё/Р»Р°С‚РµРЅС‚РЅРѕСЃС‚Рё.

### I4.S2 - Evidence pack generator

- Status: Done
- Goal: СЃРѕР±СЂР°С‚СЊ evidence pack champion/challenger СЃ СЂР°Р·РґРµР»РµРЅРёРµРј comparative Рё diagnostic РјРµС‚СЂРёРє.
- Deliverables:
  - `optimizer/evidence/*` (РіРµРЅРµСЂР°С‚РѕСЂ РѕС‚С‡РµС‚РѕРІ),
  - `docs/specs/Evidence_Pack_v0.md`,
  - РѕР±РЅРѕРІР»РµРЅРЅС‹Р№ JSON-РєРѕРЅС‚СЂР°РєС‚ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ Arena (`comparison` + `diagnostics` СЂР°Р·РґРµР»С‹).
- Acceptance Criteria:
  1. Р’ РѕС‚С‡РµС‚Рµ РѕС‚РґРµР»СЊРЅС‹Рµ СЃРµРєС†РёРё:
     - `comparison` (РґР»СЏ ranking),
     - `diagnostics` (РґР»СЏ Р»РѕРєР°Р»РёР·Р°С†РёРё bottleneck).
  2. Р”Р»СЏ РєР°Р¶РґРѕРіРѕ candidate РµСЃС‚СЊ РјРёРЅРёРјСѓРј:
     - `comparative_metrics`,
     - `diagnostic_signals_by_stage`.
  3. Р”Р»СЏ winner/challenger С„РѕСЂРјРёСЂСѓРµС‚СЃСЏ explainable diff РїРѕ comparative-РјРµС‚СЂРёРєР°Рј.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё Р·РµР»РµРЅС‹Р№ РїРѕР»РЅС‹Р№ `python -m pytest`.
- Dependencies: I4.S1.
- Risks: СЃРјРµС€РµРЅРёРµ ranking-РјРµС‚СЂРёРє Рё root-cause СЃРёРіРЅР°Р»РѕРІ РІ РѕРґРЅРѕР№ С€РєР°Р»Рµ.
- Progress (2026-05-07):
  1. Р’РІРµРґРµРЅ dual output РєРѕРЅС‚СЂР°РєС‚ РІ arena JSON: `comparison` + `diagnostics`.
  2. Р”РѕР±Р°РІР»РµРЅС‹ Р±Р°Р·РѕРІС‹Рµ stage-level diagnostic signals СЃ `bottleneck_score`.
  3. Р”РѕР±Р°РІР»РµРЅС‹ `top_bottlenecks` Рё `intervention_hints` РґР»СЏ actionable РґРёР°РіРЅРѕСЃС‚РёРєРё.
  4. Р РµР°Р»РёР·РѕРІР°РЅ РјРѕРґСѓР»СЊ `optimizer/evidence` Рё CLI РіРµРЅРµСЂР°С†РёРё Evidence Pack (`json` + `md`).
  5. Р”РѕР±Р°РІР»РµРЅ explainable winner/challenger diff Рё СЂРµРєРѕРјРµРЅРґР°С†РёРё РґР»СЏ challenger.
  6. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ + smoke СЃС†РµРЅР°СЂРёР№ `smoke_generate_evidence_pack.ps1`.

### I4.S3 - Champion export bundle

- Status: Done
- Goal: СЃС„РѕСЂРјРёСЂРѕРІР°С‚СЊ СЌРєСЃРїРѕСЂС‚РёСЂСѓРµРјС‹Р№ РїР°РєРµС‚ Р»СѓС‡С€РµР№ РєРѕРЅС„РёРіСѓСЂР°С†РёРё Рё РґРёР°РіРЅРѕСЃС‚РёС‡РµСЃРєРѕР№ РєР°СЂС‚С‹ СѓР»СѓС‡С€РµРЅРёР№.
- Deliverables:
  - bundle champion artifacts,
  - `diagnostic_map.json` (top bottlenecks + suggested interventions).
- Acceptance Criteria:
  1. Bundle РІРєР»СЋС‡Р°РµС‚ runnable config/code Рё evidence pack.
  2. Р”РёР°РіРЅРѕСЃС‚РёС‡РµСЃРєР°СЏ РєР°СЂС‚Р° СЃРѕРґРµСЂР¶РёС‚ РїСЂРёРѕСЂРёС‚РёР·РёСЂРѕРІР°РЅРЅС‹Рµ С‚РѕС‡РєРё РѕРїС‚РёРјРёР·Р°С†РёРё.
  3. Р”РѕР±Р°РІР»РµРЅС‹ integration/e2e РїСЂРѕРІРµСЂРєРё СЌРєСЃРїРѕСЂС‚РёСЂСѓРµРјРѕРіРѕ РєРѕРјРїР»РµРєС‚Р°.
- Dependencies: I4.S8.
- Risks: РїРµСЂРµРёР·Р±С‹С‚РѕС‡РЅС‹Р№ РѕР±СЉРµРј bundle Р±РµР· СЏРІРЅРѕР№ СЃС‚СЂСѓРєС‚СѓСЂС‹.
- Progress (2026-05-08):
  1. Р”РѕР±Р°РІР»РµРЅ РјРѕРґСѓР»СЊ `optimizer/champion` СЃ CLI СЌРєСЃРїРѕСЂС‚Р° champion bundle.
  2. Bundle РІРєР»СЋС‡Р°РµС‚ arena result, evidence pack, diagnostic map, winner source, winner Graph IR Рё generated agent code.
  3. Р”РѕР±Р°РІР»РµРЅ `bundle_manifest.json` РґР»СЏ reproducible handoff Р°СЂС‚РµС„Р°РєС‚РѕРІ.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё smoke-СЃРєСЂРёРїС‚ `smoke_export_champion_bundle.ps1`.

### I4.S4 - Native export contract (`langgraph_dai_native`) v0

- Status: Done
- Goal: Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ РєРѕРЅС‚СЂР°РєС‚ standalone runtime-Р°СЂС‚РµС„Р°РєС‚Р° Р±РµР· Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ `optimizer.*`.
- Deliverables:
  - `docs/adr/ADR-0019-native-langgraph-dai-export-without-optimizer-runtime.md`,
  - `docs/specs/Native_Langgraph_DAI_Export_v0.md`,
  - mapping table `Graph IR -> native langgraph-dai`.
- Acceptance Criteria:
  1. РљРѕРЅС‚СЂР°РєС‚ СЏРІРЅРѕ Р·Р°РїСЂРµС‰Р°РµС‚ `optimizer` runtime-РёРјРїРѕСЂС‚С‹ РІ exported package.
  2. РћРїРёСЃР°РЅР° СЃС‚СЂСѓРєС‚СѓСЂР° standalone package Рё entrypoint Р·Р°РїСѓСЃРєР°.
  3. РћРїРёСЃР°РЅ parity-РєРѕРЅС‚СЂР°РєС‚ `DSL path vs native exported path`.
- Dependencies: I4.S3.
- Risks: РЅРµРїРѕР»РЅРѕРµ РїРѕРєСЂС‹С‚РёРµ graph features РІ v0 mapping.
- Progress (2026-05-08):
  1. РџСЂРёРЅСЏС‚ ADR-0019 СЃ СЂР°Р·РґРµР»РµРЅРёРµРј control-plane Рё standalone runtime artifact.
  2. Р”РѕР±Р°РІР»РµРЅ spec `Native_Langgraph_DAI_Export_v0.md`.
  3. РЎРёРЅС…СЂРѕРЅРёР·РёСЂРѕРІР°РЅ roadmap РЅР° I4.S4-I4.S8.

### I4.S5 - Native renderer/codegen minimal path

- Status: Done
- Goal: СЃРіРµРЅРµСЂРёСЂРѕРІР°С‚СЊ runnable standalone Р°РіРµРЅС‚Р° РЅР° `langgraph-dai` РґР»СЏ `linear + conditional` РіСЂР°С„РѕРІ.
- Deliverables:
  - native export target РІ codegen/export pipeline,
  - standalone smoke runner.
- Acceptance Criteria:
  1. Р­РєСЃРїРѕСЂС‚РёСЂСѓРµРјС‹Р№ Р°РіРµРЅС‚ Р·Р°РїСѓСЃРєР°РµС‚СЃСЏ Р±РµР· СѓСЃС‚Р°РЅРѕРІРєРё `optimizer`.
  2. РџРѕРґРґРµСЂР¶РёРІР°СЋС‚СЃСЏ РјРёРЅРёРјСѓРј `linear + one conditional branch`.
  3. Р•СЃС‚СЊ integration/e2e smoke РїСЂРѕРІРµСЂРєР° standalone Р·Р°РїСѓСЃРєР°.
- Dependencies: I4.S4.
- Risks: drift РјРµР¶РґСѓ internal renderer Рё native runtime-РїСѓС‚РµРј.
- Progress (2026-05-08):
  1. Р РµР°Р»РёР·РѕРІР°РЅ `optimizer/champion/native_export.py` РґР»СЏ standalone native package РіРµРЅРµСЂР°С†РёРё.
  2. Champion bundle С‚РµРїРµСЂСЊ РІРєР»СЋС‡Р°РµС‚ `native_agent/` Рё РїСЂРѕРІРµСЂРєСѓ `native_runtime_smoke`.
  3. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e РїСЂРѕРІРµСЂРєРё minimal native export РїСѓС‚Рё.
  4. РџСЂРёРЅСЏС‚ ADR-0020 (minimal v0 + fallback policy РґР»СЏ unresolved `python://` refs).

### I4.S6 - Native component binding layer v0

- Status: Done
- Goal: РїРѕРґРґРµСЂР¶Р°С‚СЊ node kinds (`llm/deterministic/tool/validator/hitl_gate`) РІ native exported runtime.
- Deliverables:
  - bindings/nodes layout РґР»СЏ standalone runtime,
  - explicit contracts РґР»СЏ `python://` Рё `mcp://` refs РІ export.
- Acceptance Criteria:
  1. РљР°Р¶РґС‹Р№ РїРѕРґРґРµСЂР¶Р°РЅРЅС‹Р№ node kind РёРјРµРµС‚ native binding path.
  2. РћС€РёР±РєРё unresolved refs explainable Рё РЅРµ РјР°СЃРєРёСЂСѓСЋС‚СЃСЏ.
  3. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration С‚РµСЃС‚С‹ binding layer.
- Dependencies: I4.S5.
- Risks: С‡СЂРµР·РјРµСЂРЅР°СЏ fallback-РјР°РіРёСЏ Рё РїРѕС‚РµСЂСЏ РЅР°Р±Р»СЋРґР°РµРјРѕСЃС‚Рё РїСЂРѕР±Р»РµРј.
- Progress (2026-05-21):
  1. Native exporter/runtime expanded with `tool` binding path (`python://` callable + `mcp://` observable stub).
  2. Native compatibility preflight matrix synced: `tool` no longer blocks native target.
  3. Updated unit/integration/e2e tests and native preflight smoke scenario.
  4. Full `python -m pytest` is green (`120 passed, 1 skipped`).

### I4.S6a - Canonical DSL->Native parity for stylizer v0

- Status: Done
- Goal: РґРѕР±РёС‚СЊСЃСЏ РїР°СЂРёС‚РµС‚Р° canonical stylizer profile РјРµР¶РґСѓ DSL Рё native Р±РµР· degradation/workaround policy.
- Deliverables:
  - native binding РґР»СЏ `hitl_gate` semantics, РёСЃРїРѕР»СЊР·СѓРµРјС‹С… РІ `style_hitl_reviewer`,
  - РІС‹СЂР°РІРЅРёРІР°РЅРёРµ branch/on_fail РїРѕРІРµРґРµРЅРёСЏ РЅР° РєСЂРёС‚РёС‡РЅРѕРј demo РїСѓС‚Рё,
  - parity report РґР»СЏ canonical profile (`dsl_runtime` vs `native_runtime`).
- Acceptance Criteria:
  1. `examples/profiles/stylizer_profile_ci_v0.yaml` СѓСЃРїРµС€РЅРѕ Р·Р°РїСѓСЃРєР°РµС‚СЃСЏ РЅР° `native_runtime`.
  2. РќРµС‚ preflight block РґР»СЏ canonical profile РЅР° unsupported node kinds.
  3. РЎС‚СЂСѓРєС‚СѓСЂРЅС‹Рµ СЃРёРіРЅР°Р»С‹ РёСЃРїРѕР»РЅРµРЅРёСЏ (nodes/errors/trace topology) СЃРѕРїРѕСЃС‚Р°РІРёРјС‹ РјРµР¶РґСѓ DSL Рё native run.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ РЅР° canonical parity РїСѓС‚СЊ.
- Dependencies: I5.S2a, I4.S5.
- Risks: drift СЃРµРјР°РЅС‚РёРєРё HITL-РїРµСЂРµС…РѕРґРѕРІ РјРµР¶РґСѓ runtime-СЂРµР°Р»РёР·Р°С†РёСЏРјРё.
- Progress (2026-05-21):
  1. Native exporter/runtime СЂР°СЃС€РёСЂРµРЅ РїРѕРґРґРµСЂР¶РєРѕР№ `hitl_gate` СѓР·Р»РѕРІ Р±РµР· workaround policy.
  2. Canonical profile `examples/profiles/stylizer_profile_ci_v0.yaml` СѓСЃРїРµС€РЅРѕ Р·Р°РїСѓСЃРєР°РµС‚СЃСЏ РЅР° `native_runtime`.
  3. Preflight РґР»СЏ canonical profile Р±РѕР»СЊС€Рµ РЅРµ Р±Р»РѕРєРёСЂСѓРµС‚ native run (`incompatible_total=0`).
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e РїСЂРѕРІРµСЂРєРё hitl/native parity РїСѓС‚Рё.

### I4.S7 - DSL-vs-native parity harness + CI gate

- Status: Done
- Goal: Р°РІС‚РѕРјР°С‚РёР·РёСЂРѕРІР°С‚СЊ РїСЂРѕРІРµСЂРєСѓ СЌРєРІРёРІР°Р»РµРЅС‚РЅРѕСЃС‚Рё РёСЃРїРѕР»РЅРµРЅРёСЏ РјРµР¶РґСѓ DSL path Рё native exported path.
- Deliverables:
  - parity runner/report (`dsl_vs_native`),
  - CI gate РЅР° СЃС‚СЂСѓРєС‚СѓСЂРЅС‹Рµ СЃРёРіРЅР°Р»С‹ РІС‹РїРѕР»РЅРµРЅРёСЏ.
- Acceptance Criteria:
  1. parity РїСЂРѕРІРµСЂСЏРµС‚ `executed/skipped nodes`, `node output keys`, `errors`, `trace topology`.
  2. LLM text variability РЅРµ Р»РѕРјР°РµС‚ gate (СЃС‚СЂСѓРєС‚СѓСЂРЅР°СЏ РїСЂРѕРІРµСЂРєР°).
  3. Regression drift Р»РѕРІРёС‚СЃСЏ РІ CI.
- Dependencies: I4.S6.
- Risks: Р»РѕР¶РЅС‹Рµ positive/negative РїСЂРё СЂР°СЃС€РёСЂРµРЅРёРё runtime-РІРѕР·РјРѕР¶РЅРѕСЃС‚РµР№.
- Progress (2026-05-21):
  1. Добавлен отдельный `optimizer.parity` модуль с CLI `python -m optimizer.parity.run`.
  2. Реализован структурный comparator (`executed/skipped`, `node_output_keys`, `errors`, `trace topology`) без текстовой LLM-зависимости.
  3. Добавлен CI-gate флаг `--fail-on-mismatch` и smoke-скрипт `scripts/smoke_run_dsl_native_parity.ps1`.
  4. Добавлены unit/integration/e2e тесты parity harness.

### I4.S8 - Champion bundle default switch to native target

- Status: Done
- Goal: СЃРґРµР»Р°С‚СЊ native export РґРµС„РѕР»С‚РѕРј champion bundle.
- Deliverables:
  - bundle РІРєР»СЋС‡Р°РµС‚ `native_agent/` РєР°Рє РѕСЃРЅРѕРІРЅРѕР№ runtime artifact,
  - legacy runtime export РґРѕСЃС‚СѓРїРµРЅ С‚РѕР»СЊРєРѕ РєР°Рє optional debug fallback.
- Acceptance Criteria:
  1. Р’ bundle РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ РЅРµС‚ runtime-Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ `optimizer`.
  2. `README.bundle.md` РѕРїРёСЃС‹РІР°РµС‚ standalone Р·Р°РїСѓСЃРє native-Р°РіРµРЅС‚Р°.
  3. РџРѕР»РЅС‹Р№ РїСЂРѕРіРѕРЅ `unit + integration + e2e` green.
- Dependencies: I4.S7.
- Risks: РѕР±СЂР°С‚РЅР°СЏ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚СЊ СЃ СѓР¶Рµ СЃРѕР·РґР°РЅРЅС‹РјРё bundle.
- Progress (2026-05-22):
  1. `bundle_manifest.json` и CLI success payload получили `default_runtime_target`, `default_entrypoint_file`, `legacy_debug_entrypoint_file`.
  2. `README.bundle.md` переключен на native-first запуск, generated path оставлен как debug fallback.
  3. Интеграционные тесты обновлены под новый контракт native-first bundle.

---

## Detailed Backlog: I5-I7

### I5.S1 - Task Evaluation Profile v0

- Status: Done
- Goal: РІРІРµСЃС‚Рё config-driven РїСЂРѕС„РёР»СЊ РѕС†РµРЅРєРё РїРѕРґ РєР°Р¶РґС‹Р№ task type.
- Deliverables:
  - `docs/specs/Evaluation_Profile_v0.md`,
  - execution target contract (`dsl_runtime` / `native_runtime`),
  - typed profile schema + validator (`optimizer/evaluation/profile_*`),
  - examples РїСЂРѕС„РёР»РµР№ РґР»СЏ РјРёРЅРёРјСѓРј 2 task types.
- Acceptance Criteria:
  1. РњРѕР¶РЅРѕ Р·Р°РґР°С‚СЊ СЂР°Р·РЅС‹Рµ comparative/diagnostic РјРµС‚СЂРёРєРё РґР»СЏ СЂР°Р·РЅС‹С… Р·Р°РґР°С‡.
  2. РњРѕР¶РЅРѕ Р·Р°РґР°С‚СЊ СЂР°Р·РЅС‹Рµ evaluator chains Р±РµР· code changes.
  3. РњРѕР¶РЅРѕ Р·Р°РїСѓСЃРєР°С‚СЊ РѕРґРёРЅ Рё С‚РѕС‚ Р¶Рµ РїСЂРѕС„РёР»СЊ РЅР° `dsl_runtime` Рё `native_runtime`.
  4. Р•СЃС‚СЊ РІР°Р»РёРґР°С†РёСЏ profile contract Рё РїРѕРЅСЏС‚РЅС‹Рµ РѕС€РёР±РєРё.
- Dependencies: I4.S2.
- Risks: РёР·Р±С‹С‚РѕС‡РЅР°СЏ СЃР»РѕР¶РЅРѕСЃС‚СЊ РїСЂРѕС„РёР»СЏ РЅР° v0.
- Progress (2026-05-09):
  1. Р”РѕР±Р°РІР»РµРЅ typed РєРѕРЅС‚СЂР°РєС‚ `Evaluation Profile v0` (`profile_schema`, `profile_io`).
  2. Р”РѕР±Р°РІР»РµРЅ CLI `python -m optimizer.evaluation.run_profile`.
  3. Р РµР°Р»РёР·РѕРІР°РЅ target switch `dsl_runtime`/`native_runtime` РІ profile runner.
  4. Р”РѕР±Р°РІР»РµРЅС‹ examples profile РґР»СЏ stylizer Рё OCR/support РєРµР№СЃРѕРІ.
  5. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ + smoke-СЃРєСЂРёРїС‚ profile-run.

### I5.S2a - Native Target Compatibility Preflight v0

- Status: Done
- Goal: СЃРґРµР»Р°С‚СЊ СЏРІРЅСѓСЋ preflight-РїСЂРѕРІРµСЂРєСѓ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё profile/candidate СЃ `native_runtime` РґРѕ Р·Р°РїСѓСЃРєР°.
- Deliverables:
  - compatibility checker (`graph features` vs `native exporter capability matrix`),
  - CLI/report СЃР»РѕР№ СЃ РїРѕРґСЂРѕР±РЅС‹Рј unsupported reason РїРѕ СѓС‡Р°СЃС‚РЅРёРєР°Рј,
  - profile validation hook РґР»СЏ `native_runtime` target.
- Acceptance Criteria:
  1. РџРµСЂРµРґ native run СЃРёСЃС‚РµРјР° РІС‹РґР°РµС‚ РґРµС‚Р°Р»СЊРЅС‹Р№ РѕС‚С‡РµС‚ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё РїРѕ РєР°Р¶РґРѕРјСѓ participant.
  2. РћС€РёР±РєР° РЅРµ вЂњРїР°РґР°РµС‚ РІ СЃРµСЂРµРґРёРЅРµ РёСЃРїРѕР»РЅРµРЅРёСЏвЂќ, Р° Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ preflight СЃ РїРѕРЅСЏС‚РЅРѕР№ РїСЂРёС‡РёРЅРѕР№.
  3. Р”Р»СЏ unsupported nodes РѕС‚С‡РµС‚ СЃРѕРґРµСЂР¶РёС‚ `node_id`, `kind`, Рё recommended action.
  4. Р•СЃС‚СЊ unit/integration С‚РµСЃС‚С‹ РЅР° supported/unsupported РїСЂРѕС„РёР»Рё.
- Dependencies: I5.S1.
- Risks: СЂР°СЃСЃРёРЅС…СЂРѕРЅ capability matrix Рё С„Р°РєС‚РёС‡РµСЃРєРѕР№ РїРѕРґРґРµСЂР¶РєРё native exporter.
- Progress (2026-05-19):
  1. Р”РѕР±Р°РІР»РµРЅ `native_compatibility` РјРѕРґСѓР»СЊ СЃ profile-level preflight РѕС‚С‡РµС‚РѕРј РїРѕ participants.
  2. `run_profile --target native_runtime` С‚РµРїРµСЂСЊ Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ РґРѕ Р·Р°РїСѓСЃРєР° РїСЂРё РЅРµСЃРѕРІРјРµСЃС‚РёРјС‹С… node kinds.
  3. Р”РѕР±Р°РІР»РµРЅ structured preflight error payload (`error_type`, `preflight`) РІ stderr.
  4. Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё smoke-СЃС†РµРЅР°СЂРёР№ preflight-blocking РїРѕРІРµРґРµРЅРёСЏ.

### I5.S2b - Native Target Degradation Policy v0

- Status: Rejected
- Decision: workaround-РїРѕРґС…РѕРґ `skip_unsupported` РЅРµ СЂР°Р·РІРёРІР°РµРј; С„РѕРєСѓСЃ РЅР° РїСЂСЏРјРѕРј РїР°СЂРёС‚РµС‚Рµ DSL==Native.
- Replacement: I4.S6a (canonical parity), РґР°Р»РµРµ I4.S6/I4.S7.

### I5.S2 - Evaluator Adapter Layer v0

- Status: Planned
- Goal: РїРѕРґРєР»СЋС‡Р°С‚СЊ СЂР°Р·РЅС‹Рµ РјРµС‚РѕРґС‹ РѕС†РµРЅРєРё С‡РµСЂРµР· РµРґРёРЅС‹Р№ adapter contract.
- Deliverables:
  - evaluator adapter interface,
  - Р±Р°Р·РѕРІС‹Рµ adapters:
    - golden_oracle,
    - llm_judge,
    - executable,
    - render,
    - native_runtime_target,
  - aggregation pipeline profile-driven РјРµС‚СЂРёРє.
- Acceptance Criteria:
  1. РћРґРёРЅ Рё С‚РѕС‚ Р¶Рµ С‚СѓСЂРЅРёСЂ РјРѕР¶РµС‚ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ СЂР°Р·РЅС‹Рµ evaluator compositions.
  2. Р”Р»СЏ evaluator РјРѕР¶РЅРѕ Р·Р°РґР°РІР°С‚СЊ budget/limits РІ profile.
  3. Native exported agent РјРѕР¶РЅРѕ РїСЂРѕРіРѕРЅСЏС‚СЊ С‚РµРј Р¶Рµ evaluator pipeline.
  4. Р•СЃС‚СЊ integration tests РЅР° mixed evaluator pipeline.
- Dependencies: I4.S6a.
- Risks: РЅРµСЃРѕРіР»Р°СЃРѕРІР°РЅРЅРѕСЃС‚СЊ С€РєР°Р» РјРµР¶РґСѓ evaluator types.

### I5.S3 - Metric-Crafting Agent + HITL loop v0

- Status: Planned
- Goal: СЃРґРµР»Р°С‚СЊ РЅР°СЃС‚СЂРѕР№РєСѓ/СЌРІРѕР»СЋС†РёСЋ РјРµС‚СЂРёРє Р°РіРµРЅС‚РЅРѕР№ Р·Р°РґР°С‡РµР№ СЃ human approval.
- Deliverables:
  - metric-crafting workflow (draft -> critique -> approve),
  - HITL checkpoint contract РґР»СЏ profile activation,
  - change log РїСЂРѕС„РёР»РµР№ РјРµС‚СЂРёРє.
- Acceptance Criteria:
  1. РђРіРµРЅС‚ РјРѕР¶РµС‚ РїСЂРµРґР»РѕР¶РёС‚СЊ profile draft РґР»СЏ РЅРѕРІРѕРіРѕ РєРµР№СЃР°.
  2. Р‘РµР· HITL approve РїСЂРѕС„РёР»СЊ РЅРµ Р°РєС‚РёРІРёСЂСѓРµС‚СЃСЏ РґР»СЏ ranking.
  3. Р•СЃС‚СЊ audit trail: РєС‚Рѕ/РєРѕРіРґР°/РїРѕС‡РµРјСѓ РёР·РјРµРЅРёР» РїСЂРѕС„РёР»СЊ.
- Dependencies: I5.S1, I5.S2.
- Risks: РІС‹СЃРѕРєР°СЏ РІР°СЂРёР°С‚РёРІРЅРѕСЃС‚СЊ РєР°С‡РµСЃС‚РІР° auto-generated РјРµС‚СЂРёРє.

### I5.S4 - Post-export Native Benchmark Loop v0

- Status: Planned
- Goal: РґРѕР±Р°РІРёС‚СЊ РЅРµРїСЂРµСЂС‹РІРЅС‹Р№ benchmark-РєРѕРЅС‚СѓСЂ РґР»СЏ exported native-Р°РіРµРЅС‚Р° РїРѕСЃР»Рµ РІС‹Р±РѕСЂР° winner.
- Deliverables:
  - CLI/runner re-benchmark native artifact РїРѕ evaluation profile,
  - unified result envelope Рё comparative report (`baseline vs current`),
  - spec `docs/specs/Post_Export_Evaluation_Loop_v0.md`.
- Acceptance Criteria:
  1. Native agent РјРѕР¶РЅРѕ РїСЂРѕРіРЅР°С‚СЊ РїРѕ golden dataset С‡РµСЂРµР· РѕР±С‰РёР№ evaluation pipeline.
  2. Native agent РјРѕР¶РЅРѕ РїСЂРѕРіРЅР°С‚СЊ С‡РµСЂРµР· `llm_judge` chain (РїСЂРё РІРєР»СЋС‡РµРЅРЅРѕРј profile).
  3. РћС‚С‡РµС‚ СЃРѕРґРµСЂР¶РёС‚ comparative + diagnostic СЃРµРєС†РёРё РґР»СЏ native run.
- Dependencies: I5.S1, I5.S2.
- Risks: СЂРѕСЃС‚ СЃС‚РѕРёРјРѕСЃС‚Рё live-РїСЂРѕРіРѕРЅРѕРІ Рё РЅРµРїСЂРµРґСЃРєР°Р·СѓРµРјРѕСЃС‚СЊ LLM-judge.

### I5.S5 - Champion Regression Gates v0

- Status: Planned
- Goal: С„РѕСЂРјР°Р»РёР·РѕРІР°С‚СЊ gate policy РґР»СЏ СЂРµС€РµРЅРёСЏ `promote/rework` РїРѕСЃР»Рµ native re-benchmark.
- Deliverables:
  - gate policy contract (quality/cost/latency/failure thresholds),
  - baseline snapshot format РґР»СЏ winner export,
  - decision report (`pass/fail`, violated gates).
- Acceptance Criteria:
  1. Gate policy РїСЂРёРјРµРЅРёРјР° Рє native benchmark РѕС‚С‡РµС‚Сѓ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё.
  2. РџСЂРё РЅР°СЂСѓС€РµРЅРёРё РїРѕСЂРѕРіРѕРІ promotion Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ СЃ explainable РїСЂРёС‡РёРЅРѕР№.
  3. Р”РѕР±Р°РІР»РµРЅС‹ integration tests РЅР° positive/negative gate СЃС†РµРЅР°СЂРёРё.
- Dependencies: I5.S4.
- Risks: СЃР»РёС€РєРѕРј СЃС‚СЂРѕРіРёРµ/РјСЏРіРєРёРµ РїРѕСЂРѕРіРё Р±РµР· РґРѕРјРµРЅРЅРѕР№ РєР°Р»РёР±СЂРѕРІРєРё.

---

## Done Slices

### I0.S1 - Done

- Governance baseline docs + ADR process.
- Commit: `9579344`.

### I0.S2 - Done

- РЎРѕР·РґР°РЅ СЌС‚РѕС‚ executable backlog Рё СЃРёРЅС…СЂРѕРЅРёР·РёСЂРѕРІР°РЅС‹ СЃС‚Р°С‚СѓСЃРЅС‹Рµ РґРѕРєСѓРјРµРЅС‚С‹.
- Commit: tracked in git history.

### I0.S3 - Done

- Р”РѕР±Р°РІР»РµРЅ СЃРёРЅС…СЂРѕРЅРЅС‹Р№ demo track Рё Р·Р°С„РёРєСЃРёСЂРѕРІР°РЅР° РїРѕР»РёС‚РёРєР° РµРіРѕ РѕР±СЏР·Р°С‚РµР»СЊРЅРѕРіРѕ СЂР°Р·РІРёС‚РёСЏ.
- РџСЂРёРЅСЏС‚ ADR СЃ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Рј demo-sync РїСЂР°РІРёР»РѕРј.
- Commit: tracked in git history.

### I1.S1 - Done

- Р РµР°Р»РёР·РѕРІР°РЅС‹ typed DSL v0 schema, YAML loader, CLI-РІР°Р»РёРґР°С‚РѕСЂ Рё smoke-СЃРєСЂРёРїС‚.
- Р”РѕР±Р°РІР»РµРЅС‹ 3 РІР°Р»РёРґРЅС‹С… СЂРµС„РµСЂРµРЅСЃРЅС‹С… СЃРїРµС†РёС„РёРєР°С†РёРё: `direct_llm`, `ocr_first`, `hitl_gate`.
- Commit: tracked in git history.

### I1.S2 - Done

- Р РµР°Р»РёР·РѕРІР°РЅС‹ runtime-neutral Graph IR models + validators + CLI.
- Р”РѕР±Р°РІР»РµРЅС‹ edge/start/end/unreachable РїСЂРѕРІРµСЂРєРё Рё roundtrip СЃРµСЂРёР°Р»РёР·Р°С†РёСЏ.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ РґР»СЏ Graph IR Рё smoke-СЃРєСЂРёРїС‚.
- Commit: tracked in git history.

### I1.S3 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ РєРѕРјРїРёР»СЏС‚РѕСЂ DSL -> Graph IR СЃ compile report.
- Р”РѕР±Р°РІР»РµРЅС‹ CLI РєРѕРјРїРёР»СЏС†РёРё Рё smoke-СЃРєСЂРёРїС‚ СЃРєРІРѕР·РЅРѕР№ РєРѕРјРїРёР»СЏС†РёРё DSL-РїСЂРёРјРµСЂРѕРІ.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ РЅР° success/failure compile path.
- Commit: tracked in git history.

### I2.S1 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ runtime renderer Graph IR -> BaseWorkflow (langgraph-dai).
- Р”РѕР±Р°РІР»РµРЅ runtime CLI Рё smoke demo Р·Р°РїСѓСЃРє workflow.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ СЂРµРЅРґРµСЂРµСЂР° Рё branch-Р»РѕРіРёРєРё.
- Commit: tracked in git history.

### I2.S2 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ codegen-РїСѓС‚СЊ DSL/IR -> runnable Python package Р°РіРµРЅС‚Р°.
- Р”РѕР±Р°РІР»РµРЅ CLI РіРµРЅРµСЂР°С†РёРё `python -m optimizer.codegen.generate`.
- Р”РѕР±Р°РІР»РµРЅ smoke demo РіРµРЅРµСЂР°С†РёРё Рё Р·Р°РїСѓСЃРєР° СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅРѕРіРѕ Р°РіРµРЅС‚Р°.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ РЅРѕРІРѕРіРѕ С„СѓРЅРєС†РёРѕРЅР°Р»Р°.
- Commit: tracked in git history.

### I2.S3 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ white-box trace v0 СЃ node-level СЃРѕР±С‹С‚РёСЏРјРё `started/completed/failed/skipped`.
- Р”РѕР±Р°РІР»РµРЅ `InMemoryTraceStore` Рё Р°РіСЂРµРіРёСЂРѕРІР°РЅРЅР°СЏ `trace_summary` РїРѕ run/task.
- Runtime Рё CLI С‚РµРїРµСЂСЊ РІРѕР·РІСЂР°С‰Р°СЋС‚ `node_events` + `trace_summary`.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration С‚РµСЃС‚С‹ trace-РєРѕРЅС‚СЂР°РєС‚Р°.
- Commit: tracked in git history.

### I2.S4 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ checkpoint/resume РєРѕРЅС‚СЂР°РєС‚ СЃ С„Р°Р№Р»РѕРІС‹Рј checkpoint-store.
- Р”РѕР±Р°РІР»РµРЅ invoke/resume РїСѓС‚СЊ РІ runtime API Рё CLI (`--resume-task-id`, `--checkpoint-dir`).
- Р”РѕР±Р°РІР»РµРЅС‹ integration/negative С‚РµСЃС‚С‹ РЅР° missing/invalid task_id.
- Р”РѕР±Р°РІР»РµРЅ smoke invoke->resume СЃС†РµРЅР°СЂРёР№ РІ runtime demo.
- Commit: tracked in git history.

### I3.S1 - Done

- Р’РІРµРґРµРЅ Golden Dataset JSONL РєРѕРЅС‚СЂР°РєС‚ (`case_id`, `input`, `expected`, `tags`, `metadata`).
- Р РµР°Р»РёР·РѕРІР°РЅ typed loader СЃ РґРёР°РіРЅРѕСЃС‚РёРєРѕР№ РѕС€РёР±РѕРє РїРѕ line number.
- Р”РѕР±Р°РІР»РµРЅ CLI `python -m optimizer.evaluation.validate_dataset`.
- Р”РѕР±Р°РІР»РµРЅ smoke-СЃРєСЂРёРїС‚ РІР°Р»РёРґР°С†РёРё РґР°С‚Р°СЃРµС‚Р° Рё РїРѕРєСЂС‹С‚РёРµ unit/integration/e2e.
- Commit: tracked in git history.

### I3.S2 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ executable oracle runner РЅР° Р±Р°Р·Рµ `must_include/forbidden` РїСЂР°РІРёР».
- Р”РѕР±Р°РІР»РµРЅ CLI `python -m optimizer.evaluation.run_oracle` Рё smoke-СЃРєСЂРёРїС‚ oracle РїСЂРѕРіРѕРЅР°.
- Р”РѕР±Р°РІР»РµРЅС‹ deterministic (`expected_stub`) Рё runtime РїСѓС‚Рё РёСЃРїРѕР»РЅРµРЅРёСЏ.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ Рё Р·РµР»РµРЅС‹Р№ full pytest gate.
- Commit: tracked in git history.

### I3.S3 - Done

- Р РµР°Р»РёР·РѕРІР°РЅ Architecture Arena v0 РґР»СЏ СЃСЂР°РІРЅРµРЅРёСЏ 2-3 Р°СЂС…РёС‚РµРєС‚СѓСЂ.
- Р’РІРµРґРµРЅ equal-budget policy `equal_cases` СЃ РµРґРёРЅС‹Рј РЅР°Р±РѕСЂРѕРј РєРµР№СЃРѕРІ РґР»СЏ РІСЃРµС… СѓС‡Р°СЃС‚РЅРёРєРѕРІ.
- Р”РѕР±Р°РІР»РµРЅ CLI `python -m optimizer.arena.run_tournament`, example tournament config Рё smoke-СЃРєСЂРёРїС‚.
- Р”РѕР±Р°РІР»РµРЅС‹ unit/integration/e2e С‚РµСЃС‚С‹ arena-РєРѕРЅС‚СѓСЂР°.
- Commit: tracked in git history.
