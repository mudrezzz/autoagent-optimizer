# Roadmap

## Status Legend

- `Planned` - слайс запланирован, не начат.
- `In Progress` - слайс в работе.
- `Done` - слайс завершен и закоммичен.
- `Blocked` - есть внешний блокер.

## Delivery Model

Разработка идет итеративно малыми слайсами с постоянной поставкой проверяемой ценности:

- MVP-1: Foundation + executable core loop.
- MVP-2: Optimization depth + diagnostics.
- MVP-3: Team-grade operations + extensibility.

Принцип: расширяем концентрическими кругами, а не строим длинную линейную фазу.

## Execution Shift (Roadmap v3)

Начиная с текущего окна, работа ведется вертикальными продуктовыми слайсами:

1. Каждый слайс включает `Backend + Frontend + Demo + QA`.
2. Функциональность развивается вширь по capability, а не последовательно по слоям системы.
3. Любая backend-возможность считается незавершенной, пока не проверяется через UI и e2e путь.
4. Любой frontend-слайс обязан соблюдать `design_system` как обязательный стандарт интерфейса.
5. UX-каркас frontend собирается по North Star референсу [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png) и правилам [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md).

### Capability Matrix (single source of truth)

| Capability | Scope | Status Axes |
|---|---|---|
| C1 | Battle Registry | `BE / FE / Demo / QA` |
| C2 | Task Chat + Candidate Generation | `BE / FE / Demo / QA` |
| C3 | Pattern Library + RAG Retrieval | `BE / FE / Demo / QA` |
| C4 | Dataset Studio | `BE / FE / Demo / QA` |
| C5 | Metrics Studio | `BE / FE / Demo / QA` |
| C6 | Evaluators Studio | `BE / FE / Demo / QA` |
| C7 | Optimizer Run Monitor | `BE / FE / Demo / QA` |
| C8 | Report + Champion Export/Import | `BE / FE / Demo / QA` |

Legacy note: исторические DSL-first слайсы (validate/compile/run/arena/evidence/champion) остаются частью foundation, но больше не являются пользовательской capability-моделью.
Transition note: текущий UI пока использует legacy ярлыки (`C4 Dataset & Metrics`, `C5 Optimizer`, `C6 Report`), миграция выполняется в `V2.4.*`.

---

## MVP-1 (Core Loop)

Цель: получить рабочий путь `DSL -> Graph IR -> LangGraph runtime -> evaluation -> evidence`.

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

Цель: сделать оценку конфигурируемой под задачу, добавить MetricOps/HITL контур и углубить оптимизацию.

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

Note: после `V2.3.S1` добавлен corrective slice `V2.3.S1a`, чтобы зафиксировать SaaS IA:
`Battles Hub` (список battle-проектов клиента) отдельно от `Battle Workspace` (рабочий экран battle-проекта).

| Slice | Description | Status | Output |
|---|---|---|---|
| V2.3.S1 | C1 Workspace & Project Registry vertical slice | Done | workspace list/create/open + project list/create/open + FE/BE/e2e |
| V2.3.S1a | SaaS IA split: Battles Hub vs Battle Workspace | Done | separate screens, sticky app-shell behavior, no right rail on Battles Hub, capability menu only inside Battle Workspace |
| V2.3.S2 | C2 Battle Chat brief-to-candidates v0 | Done | arena-scoped chat state + candidate draft generation + FE/BE/demo/QA |
| V2.3.S2b | C1/C2 Battle Domain Correction | Done | arena-first API (`/api/arenas/*`), Battles Hub naming, Battle Workspace layout (`center candidates + right chat`) |
| V2.3.S2c | C2 UX polish: classic chat + readable candidate rows | Done | right rail converted to classic chat UX; center candidates rendered as metric rows aligned with app-v3 visual language |
| V2.3.S2d | C2 candidate accordion details | Done | expandable rows with architecture details, mini-diagram and architecture logo |
| V2.3.S3 | C3 Pattern Library + RAG controls v0 | Done | pattern browse/search + selection controls + retrieval trace |
| V2.3.S4 | Candidate assembly + internal compile readiness | Done | candidate checkbox selection + `POST /api/arenas/{id}/candidates/select-for-tests` + internal retries/auto-fix before issue + FE/BE/QA |
| V2.3.S4a | UX corrective: unified checkbox selection (C2/C3) | Done | C3 switched to single checkbox per pattern + explicit `Save`; interaction aligned with C2 selection flow |
| V2.3.S5 | C4 Dataset Studio v0 | Done | upload/manual/synthetic/clean/check flows + versioned dataset artifacts |
| V2.3.S5a | C4 UX unification + Dataset Editor | Done | candidate-like dataset list with checkbox+Save assignment, details preview rows, dedicated editor screen with breadcrumbs and row-level editing/import |
| V2.3.S6 | C4 Metrics & Evaluators Studio v0 | Done | configurable comparative/diagnostic metrics + evaluator method selection |
| V2.3.S6a | C4 corrective UX: separate Metrics tab + wiki real screenshots policy | Done | C4 split into `Datasets`/`Metrics` tabs, targeted FE/BE regression tests, real C4/C5 screenshots in user docs |
| V2.3.S7 | C5 Optimizer setup + budget/epoch controls | Done | optimization method settings + budget limits + launch guardrails |
| V2.3.S8 | C5 Run Monitor + version manifest timeline | Planned | progress/epochs/events/trace drilldown + run manifest visibility |
| V2.3.S9 | C6 Report + Champion export/import loop | Planned | final report view + champion export + native import + re-benchmark trigger |

### Iteration V2.4 - Wizard IA + Evaluation Decoupling

Цель: перейти от простого меню к последовательному capability-wizard и развести `datasets`, `metrics`, `evaluators` в отдельные продуктовые шаги.

| Slice | Description | Status | Output |
|---|---|---|---|
| V2.4.S1 | Wizard Engine v0 (menu as stateful flow) | Done | unlock/lock DAG по шагам, статусы `locked/available/in_progress/completed/blocked` |
| V2.4.S2 | IA split: C4 Datasets / C5 Metrics / C6 Evaluators | Done | отдельные пункты меню и экраны, без смешения потоков |
| V2.4.S3 | Candidate-feature-aware metrics availability | Planned | автодоступность метрик по структуре выбранных кандидатов |
| V2.4.S4 | Evaluator x Metric matrix v0 | Planned | матричная настройка оценивания и preflight-проверка покрытия |
| V2.4.S5 | Dataset v2 schema (stage-aware targets) | Planned | поддержка retrieval/rerank/synthesis/final target типов и соответствующих expected-структур |
| V2.4.S6 | Contextual right chat (tab-scoped copilot) | Planned | чат адаптируется к активной capability и выбранной сущности |
| V2.4.S7 | Runtime snapshot UX cleanup | Planned | перенос snapshot в debug drawer/dev-tools, без перекрытия основного контента |

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

Цель: сделать систему удобной для командной и длительной эксплуатации.

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

1. Планируем только ближайшие 1-2 итерации детально.
2. Каждый слайс должен быть реалистично завершен за 0.5-2 дня.
3. Слайс закрывается только при выполнении вертикального DoD:
   - backend изменение,
   - frontend проверяемый surface,
   - frontend соответствует `design_system` (tokens/components/voice),
   - demo-сценарий,
   - тесты (unit/integration/e2e) на затронутый путь.
4. После каждого слайса сразу обновляем:
   - `Roadmap.md`
   - `README.md`
   - `System_Architecture_Overview.md` (если менялась архитектура)
   - `docs/adr/*` (если было архитектурное решение)
   - `docs/wiki/*` (обязательное пользовательское и developer обновление по слайсу)
5. Каждый слайс фиксируется отдельным commit.
6. Перед commit обязателен тест-гейт по типу слайса:
   - `Fast gate`: frontend-only микроизменения (`python -m pytest tests/unit/test_frontend_contracts.py` + `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`),
   - `Targeted gate`: frontend + API-срез (fast gate + `python -m pytest tests/integration/test_frontend_dev_server.py` + профильные integration/e2e),
   - `Full gate`: крупные слайсы/release (`python -m pytest`).
7. При фронтовых изменениях в описании слайса фиксируем, какие артефакты `design_system` использованы
   (`colors_and_type.css`, `ui_kits/*`, `assets/*`, copy rules).
8. При фронтовых изменениях также фиксируем соответствие UX North Star (`app-v3`: трехколоночный layout, run-centric header, KPI->architectures->trace, intervention rail).
9. Wiki публикуется в GitHub Pages из текущего репозитория; для каждого закрытого слайса обязателен release-note в `docs/wiki/releases/*`.
10. Любой UI-слайс обязан обновлять **реальные** скриншоты в `docs/wiki/assets/screenshots/*` и ссылки на них в `docs/wiki/user_guides/*`.

## Backlog Source

Детализированный исполнимый backlog:

- [docs/backlog/Executable_Slice_Backlog.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)

## Demo Track

Синхронный демо-трек проекта:

- [docs/demo/Demo_Track.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)

## Wiki

Пользовательская и developer документация (GitHub Pages source):

- [docs/wiki/index.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/wiki/index.md)

