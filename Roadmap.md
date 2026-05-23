# Roadmap

## Status Legend

- `Planned` - СЃР»Р°Р№СЃ Р·Р°РїР»Р°РЅРёСЂРѕРІР°РЅ, РЅРµ РЅР°С‡Р°С‚.
- `In Progress` - СЃР»Р°Р№СЃ РІ СЂР°Р±РѕС‚Рµ.
- `Done` - СЃР»Р°Р№СЃ Р·Р°РІРµСЂС€РµРЅ Рё Р·Р°РєРѕРјРјРёС‡РµРЅ.
- `Blocked` - РµСЃС‚СЊ РІРЅРµС€РЅРёР№ Р±Р»РѕРєРµСЂ.

## Delivery Model

Р Р°Р·СЂР°Р±РѕС‚РєР° РёРґРµС‚ РёС‚РµСЂР°С‚РёРІРЅРѕ РјР°Р»С‹РјРё СЃР»Р°Р№СЃР°РјРё СЃ РїРѕСЃС‚РѕСЏРЅРЅРѕР№ РїРѕСЃС‚Р°РІРєРѕР№ РїСЂРѕРІРµСЂСЏРµРјРѕР№ С†РµРЅРЅРѕСЃС‚Рё:

- MVP-1: Foundation + executable core loop.
- MVP-2: Optimization depth + diagnostics.
- MVP-3: Team-grade operations + extensibility.

РџСЂРёРЅС†РёРї: СЂР°СЃС€РёСЂСЏРµРј РєРѕРЅС†РµРЅС‚СЂРёС‡РµСЃРєРёРјРё РєСЂСѓРіР°РјРё, Р° РЅРµ СЃС‚СЂРѕРёРј РґР»РёРЅРЅСѓСЋ Р»РёРЅРµР№РЅСѓСЋ С„Р°Р·Сѓ.

## Execution Shift (Roadmap v3)

РќР°С‡РёРЅР°СЏ СЃ С‚РµРєСѓС‰РµРіРѕ РѕРєРЅР°, СЂР°Р±РѕС‚Р° РІРµРґРµС‚СЃСЏ РІРµСЂС‚РёРєР°Р»СЊРЅС‹РјРё РїСЂРѕРґСѓРєС‚РѕРІС‹РјРё СЃР»Р°Р№СЃР°РјРё:

1. РљР°Р¶РґС‹Р№ СЃР»Р°Р№СЃ РІРєР»СЋС‡Р°РµС‚ `Backend + Frontend + Demo + QA`.
2. Р¤СѓРЅРєС†РёРѕРЅР°Р»СЊРЅРѕСЃС‚СЊ СЂР°Р·РІРёРІР°РµС‚СЃСЏ РІС€РёСЂСЊ РїРѕ capability, Р° РЅРµ РїРѕСЃР»РµРґРѕРІР°С‚РµР»СЊРЅРѕ РїРѕ СЃР»РѕСЏРј СЃРёСЃС‚РµРјС‹.
3. Р›СЋР±Р°СЏ backend-РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊ СЃС‡РёС‚Р°РµС‚СЃСЏ РЅРµР·Р°РІРµСЂС€РµРЅРЅРѕР№, РїРѕРєР° РЅРµ РїСЂРѕРІРµСЂСЏРµС‚СЃСЏ С‡РµСЂРµР· UI Рё e2e РїСѓС‚СЊ.
4. Р›СЋР±РѕР№ frontend-СЃР»Р°Р№СЃ РѕР±СЏР·Р°РЅ СЃРѕР±Р»СЋРґР°С‚СЊ `design_system` РєР°Рє РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ СЃС‚Р°РЅРґР°СЂС‚ РёРЅС‚РµСЂС„РµР№СЃР°.
5. UX-РєР°СЂРєР°СЃ frontend СЃРѕР±РёСЂР°РµС‚СЃСЏ РїРѕ North Star СЂРµС„РµСЂРµРЅСЃСѓ [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png) Рё РїСЂР°РІРёР»Р°Рј [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md).

### Capability Matrix (single source of truth)

| Capability | Scope | Status Axes |
|---|---|---|
| C1 | Battle Registry | `BE / FE / Demo / QA` |
| C2 | Task Chat + Candidate Generation | `BE / FE / Demo / QA` |
| C3 | Pattern Library + RAG Retrieval | `BE / FE / Demo / QA` |
| C4 | Dataset & Metrics Studio | `BE / FE / Demo / QA` |
| C5 | Optimizer Run Monitor | `BE / FE / Demo / QA` |
| C6 | Report + Champion Export/Import | `BE / FE / Demo / QA` |

Legacy note: РёСЃС‚РѕСЂРёС‡РµСЃРєРёРµ DSL-first СЃР»Р°Р№СЃС‹ (validate/compile/run/arena/evidence/champion) РѕСЃС‚Р°СЋС‚СЃСЏ С‡Р°СЃС‚СЊСЋ foundation, РЅРѕ Р±РѕР»СЊС€Рµ РЅРµ СЏРІР»СЏСЋС‚СЃСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРѕР№ capability-РјРѕРґРµР»СЊСЋ.

---

## MVP-1 (Core Loop)

Р¦РµР»СЊ: РїРѕР»СѓС‡РёС‚СЊ СЂР°Р±РѕС‡РёР№ РїСѓС‚СЊ `DSL -> Graph IR -> LangGraph runtime -> evaluation -> evidence`.

### Iteration I0 - Governance & Baseline

| Slice | Description | Status | Output |
|---|---|---|---|
| I0.S1 | Project governance docs baseline | Done | README + Roadmap + Architecture + ADR process |
| I0.S2 | Initial backlog shaping from TZ to executable slices | Done | prioritized slice backlog |
| I0.S3 | Continuous demo track baseline and policy | Done | demo scenario + ADR + process rules |

### Iteration I1 - DSL/IR Skeleton

| Slice | Description | Status | Output |
|---|---|---|---|
| I1.S1 | DSL v0 schema draft (YAML-first) | Done | `dsl/schema` + examples |
| I1.S2 | Graph IR v0 typed model | Done | runtime-neutral IR contracts |
| I1.S3 | DSL -> IR compiler v0 | Done | parser/validator + compile report |

### Iteration I2 - Runtime Rendering

| Slice | Description | Status | Output |
|---|---|---|---|
| I2.S1 | LangGraph renderer adapter on top of `langgraph-dai` | Done | IR -> BaseWorkflow |
| I2.S2 | Agent code generation v0 (DSL/IR -> runnable Python package) | Done | generated agent artifact + runner |
| I2.S3 | Node event capture + white-box trace v0 | Done | node-level events/logs + run summary |
| I2.S4 | Resume/checkpoint contract path | Done | invoke/resume reliability |

### Iteration I3 - Evaluation + Arena Lite

| Slice | Description | Status | Output |
|---|---|---|---|
| I3.S1 | Golden dataset JSONL + loader | Done | dataset contract + loader + CLI |
| I3.S2 | Executable oracle runner (schema/pytest) | Done | deterministic evaluation |
| I3.S3 | Architecture Arena equal-budget tournament v0 | Done | baseline comparison report |

### Iteration I4 - Evidence + Export

| Slice | Description | Status | Output |
|---|---|---|---|
| I4.S1 | Middle-metrics v0 | Done | per-node quality/cost/latency metrics + composite scoring |
| I4.S2a | Stylizer demo scale + budget profiles (smoke/full) | Done | dataset v1 expanded, arena smoke/full configs, cheap live defaults |
| I4.S2 | Evidence Pack v0 + dual-metrics contract | Done | comparative vs diagnostic evidence report |
| I4.S2b | Run-policy split: smoke-live vs decision-live | Done | dedicated decision budget profile + quality-model run path |
| I4.S3 | Champion export bundle v0 | Done | deployable artifact set |
| I4.S4 | Native export contract (`langgraph_dai_native`) v0 | Done | standalone runtime artifact spec + mapping rules |
| I4.S5 | Native renderer/codegen minimal path | Done | runnable standalone agent (`linear + conditional`) |
| I4.S6a | Canonical DSL->Native Parity (HITL semantics) v0 | Done | canonical stylizer profile runs on native without workaround policies |
| I4.S6 | Native component binding layer v0 | Done | llm/deterministic/tool/validator/hitl bindings without `optimizer` runtime |
| I4.S7 | DSL-vs-native parity harness + CI gate | Done | structural parity report and regression guard |
| I4.S8 | Champion bundle default switch to native target | Done | native-first bundle, legacy runtime path as optional debug fallback |

---

## MVP-2 (Evaluation Fabric, Optimization & Components)

Р¦РµР»СЊ: СЃРґРµР»Р°С‚СЊ РѕС†РµРЅРєСѓ РєРѕРЅС„РёРіСѓСЂРёСЂСѓРµРјРѕР№ РїРѕРґ Р·Р°РґР°С‡Сѓ, РґРѕР±Р°РІРёС‚СЊ MetricOps/HITL РєРѕРЅС‚СѓСЂ Рё СѓРіР»СѓР±РёС‚СЊ РѕРїС‚РёРјРёР·Р°С†РёСЋ.

### Iteration V2.1 - Legacy Capability Shell Foundation

| Slice | Description | Status | Output |
|---|---|---|---|
| V2.1.S1 | UI shell + API contract skeleton for legacy C1-C6 | Done | frontend shell + lightweight API (`legacy C1 real`, `legacy C2..C6 stub`) + smoke/e2e checks |
| V2.1.S2 | Legacy C1 vertical slice | Done | app-v3-aligned workbench shell + real DSL validate/compile + compile-report/diagnostics visible in UI |
| V2.1.S3a | React/TypeScript migration baseline | Done | Vite + React/TS toolchain, migrated legacy C1 workbench UI, Python dev server serves `frontend/dist` |
| V2.1.S3 | Legacy C2 vertical slice | Planned | runtime run + trace explorer in UI |
| V2.1.S4 | Legacy C4 vertical slice (smoke budget) | Planned | arena ranking/winner visible in UI |
| V2.1.S5 | Legacy C6 read-only vertical slice | Planned | bundle inspector in UI (manifest/parity/evidence) |

### Iteration V2.2 - Evaluation Fabric Expansion (Backend-heavy)

| Slice | Description | Status | Output |
|---|---|---|---|
| V2.2.S1 | Evaluator adapters foundation | Planned | profile runner + pluggable evaluators (`golden`/`llm_judge`/`executable`/`render`) |
| V2.2.S2 | Comparative vs diagnostics UI surfacing | Planned | comparative/diagnostic panels in UI |
| V2.2.S3 | Champion export/import loop surface | Planned | export trigger + native import entry + re-benchmark hook |
| V2.2.S4 | Unified budget controls | Planned | smoke/decision/full presets across run surfaces |
| V2.2.S5 | One-click end-to-end demo path | Planned | guided scenario with deterministic checks and saved artifacts |

### Iteration V2.3 - Product Realignment Vertical Slices (Primary)

Note: РїРѕСЃР»Рµ `V2.3.S1` РґРѕР±Р°РІР»РµРЅ corrective slice `V2.3.S1a`, С‡С‚РѕР±С‹ Р·Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ SaaS IA:
`Projects Hub` (СЃРїРёСЃРѕРє РїСЂРѕРµРєС‚РѕРІ РєР»РёРµРЅС‚Р°) РѕС‚РґРµР»СЊРЅРѕ РѕС‚ `Project Workspace` (СЂР°Р±РѕС‡РёР№ СЌРєСЂР°РЅ РїСЂРѕРµРєС‚Р°).

| Slice | Description | Status | Output |
|---|---|---|---|
| V2.3.S1 | C1 Workspace & Project Registry vertical slice | Done | workspace list/create/open + project list/create/open + FE/BE/e2e |
| V2.3.S1a | SaaS IA split: Projects Hub vs Project Workspace | Done | separate screens, sticky app-shell behavior, no right rail on Projects Hub, capability menu only inside Project Workspace |
| V2.3.S2 | C2 Project Chat brief-to-candidates v0 | Done | project-scoped chat state + candidate draft generation + FE/BE/demo/QA |
| V2.3.S2b | C1/C2 Battle Domain Correction | Done | arena-first API (`/api/arenas/*`), Battles Hub naming, Battle Workspace layout (`center candidates + right chat`) |
| V2.3.S3 | C3 Pattern Library + RAG controls v0 | Planned | pattern browse/search + include/exclude + retrieval trace |
| V2.3.S4 | Candidate assembly + internal compile readiness | Planned | candidate graph build + compile/validate gate + ready status |
| V2.3.S5 | C4 Dataset Studio v0 | Planned | upload/manual/synthetic/clean/check flows + versioned dataset artifacts |
| V2.3.S6 | C4 Metrics & Evaluators Studio v0 | Planned | configurable comparative/diagnostic metrics + evaluator method selection |
| V2.3.S7 | C5 Optimizer setup + budget/epoch controls | Planned | optimization method settings + budget limits + launch guardrails |
| V2.3.S8 | C5 Run Monitor + version manifest timeline | Planned | progress/epochs/events/trace drilldown + run manifest visibility |
| V2.3.S9 | C6 Report + Champion export/import loop | Planned | final report view + champion export + native import + re-benchmark trigger |

### Iteration I5 - Evaluation Fabric & MetricOps

| Slice | Description | Status | Output |
|---|---|---|---|
| I5.S1 | Task Evaluation Profile v0 | Done | config contract for task-specific metrics/evaluators/gates + execution targets |
| I5.S2a | Native Target Compatibility Preflight v0 | Done | profile preflight for native target + explicit unsupported-node report |
| I5.S2 | Evaluator Adapter Layer v0 | Planned | pluggable evaluators (golden / llm_judge / executable / render) + native runtime adapter |
| I5.S3 | Metric-Crafting Agent + HITL loop v0 | Planned | agent-proposed metrics with human approval checkpoints |
| I5.S4 | Post-export Native Benchmark Loop v0 | Planned | benchmark exported native agent over golden/llm_judge pipeline |
| I5.S5 | Champion Regression Gates v0 | Planned | baseline-vs-current gating for exported native artifacts |

### Iteration I6 - Component Contracts

| Slice | Description | Status | Output |
|---|---|---|---|
| I6.S1 | Component contract spec v0 | Planned | IO schema + invariants + permissions |
| I6.S2 | Component registry lite | Planned | versions + test status + approvals |
| I6.S3 | User component intake (python/http/mcp wrappers) | Planned | candidate component onboarding |

### Iteration I7 - Optimizer Depth

| Slice | Description | Status | Output |
|---|---|---|---|
| I7.S1 | Config search policies (random/grid/optuna) | Planned | deep optimization rounds |
| I7.S2 | Promote/prune + budget allocator | Planned | architecture family progression |
| I7.S3 | Intervention operators v0 (diagnostic-driven) | Planned | targeted bottleneck fixes from diagnostic signals |

---

## MVP-3 (Operational Maturity)

Р¦РµР»СЊ: СЃРґРµР»Р°С‚СЊ СЃРёСЃС‚РµРјСѓ СѓРґРѕР±РЅРѕР№ РґР»СЏ РєРѕРјР°РЅРґРЅРѕР№ Рё РґР»РёС‚РµР»СЊРЅРѕР№ СЌРєСЃРїР»СѓР°С‚Р°С†РёРё.

### Iteration I8 - Team Readiness

| Slice | Description | Status | Output |
|---|---|---|---|
| I8.S1 | HITL checkpoints orchestration hardening | Planned | explicit approval flow |
| I8.S2 | Policy gates + permission enforcement | Planned | governance/security constraints |
| I8.S3 | Reproducible run manifests | Planned | deterministic reruns |

### Iteration I9 - UX & Operability

| Slice | Description | Status | Output |
|---|---|---|---|
| I9.S1 | CLI ergonomics for full lifecycle | Planned | create/run/compare/export commands |
| I9.S2 | Observability summaries + dashboards (lite) | Planned | quick diagnosis surface |
| I9.S3 | Onboarding quickstart for new developers | Planned | 15-minute project entry |

---

## Working Agreement Per Iteration

1. РџР»Р°РЅРёСЂСѓРµРј С‚РѕР»СЊРєРѕ Р±Р»РёР¶Р°Р№С€РёРµ 1-2 РёС‚РµСЂР°С†РёРё РґРµС‚Р°Р»СЊРЅРѕ.
2. РљР°Р¶РґС‹Р№ СЃР»Р°Р№СЃ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ СЂРµР°Р»РёСЃС‚РёС‡РЅРѕ Р·Р°РІРµСЂС€РµРЅ Р·Р° 0.5-2 РґРЅСЏ.
3. РЎР»Р°Р№СЃ Р·Р°РєСЂС‹РІР°РµС‚СЃСЏ С‚РѕР»СЊРєРѕ РїСЂРё РІС‹РїРѕР»РЅРµРЅРёРё РІРµСЂС‚РёРєР°Р»СЊРЅРѕРіРѕ DoD:
   - backend РёР·РјРµРЅРµРЅРёРµ,
   - frontend РїСЂРѕРІРµСЂСЏРµРјС‹Р№ surface,
   - frontend СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓРµС‚ `design_system` (tokens/components/voice),
   - demo-СЃС†РµРЅР°СЂРёР№,
   - С‚РµСЃС‚С‹ (unit/integration/e2e) РЅР° Р·Р°С‚СЂРѕРЅСѓС‚С‹Р№ РїСѓС‚СЊ.
4. РџРѕСЃР»Рµ РєР°Р¶РґРѕРіРѕ СЃР»Р°Р№СЃР° СЃСЂР°Р·Сѓ РѕР±РЅРѕРІР»СЏРµРј:
   - `Roadmap.md`
   - `README.md`
   - `System_Architecture_Overview.md` (РµСЃР»Рё РјРµРЅСЏР»Р°СЃСЊ Р°СЂС…РёС‚РµРєС‚СѓСЂР°)
   - `docs/adr/*` (РµСЃР»Рё Р±С‹Р»Рѕ Р°СЂС…РёС‚РµРєС‚СѓСЂРЅРѕРµ СЂРµС€РµРЅРёРµ)
5. РљР°Р¶РґС‹Р№ СЃР»Р°Р№СЃ С„РёРєСЃРёСЂСѓРµС‚СЃСЏ РѕС‚РґРµР»СЊРЅС‹Рј commit.
6. РџРµСЂРµРґ commit РѕР±СЏР·Р°С‚РµР»РµРЅ С‚РµСЃС‚-РіРµР№С‚ РїРѕ С‚РёРїСѓ СЃР»Р°Р№СЃР°:
   - `Fast gate`: frontend-only РјРёРєСЂРѕРёР·РјРµРЅРµРЅРёСЏ (`python -m pytest tests/unit/test_frontend_contracts.py` + `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`),
   - `Targeted gate`: frontend + API-СЃСЂРµР· (fast gate + `python -m pytest tests/integration/test_frontend_dev_server.py` + РїСЂРѕС„РёР»СЊРЅС‹Рµ integration/e2e),
   - `Full gate`: РєСЂСѓРїРЅС‹Рµ СЃР»Р°Р№СЃС‹/release (`python -m pytest`).
7. РџСЂРё С„СЂРѕРЅС‚РѕРІС‹С… РёР·РјРµРЅРµРЅРёСЏС… РІ РѕРїРёСЃР°РЅРёРё СЃР»Р°Р№СЃР° С„РёРєСЃРёСЂСѓРµРј, РєР°РєРёРµ Р°СЂС‚РµС„Р°РєС‚С‹ `design_system` РёСЃРїРѕР»СЊР·РѕРІР°РЅС‹
   (`colors_and_type.css`, `ui_kits/*`, `assets/*`, copy rules).
8. РџСЂРё С„СЂРѕРЅС‚РѕРІС‹С… РёР·РјРµРЅРµРЅРёСЏС… С‚Р°РєР¶Рµ С„РёРєСЃРёСЂСѓРµРј СЃРѕРѕС‚РІРµС‚СЃС‚РІРёРµ UX North Star (`app-v3`: С‚СЂРµС…РєРѕР»РѕРЅРѕС‡РЅС‹Р№ layout, run-centric header, KPI->architectures->trace, intervention rail).

## Backlog Source

Р”РµС‚Р°Р»РёР·РёСЂРѕРІР°РЅРЅС‹Р№ РёСЃРїРѕР»РЅРёРјС‹Р№ backlog:

- [docs/backlog/Executable_Slice_Backlog.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)

## Demo Track

РЎРёРЅС…СЂРѕРЅРЅС‹Р№ РґРµРјРѕ-С‚СЂРµРє РїСЂРѕРµРєС‚Р°:

- [docs/demo/Demo_Track.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)

