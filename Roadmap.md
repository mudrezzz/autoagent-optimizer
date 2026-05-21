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
| I4.S8 | Champion bundle default switch to native target | Planned | native-first bundle, legacy runtime path as optional debug fallback |

---

## MVP-2 (Evaluation Fabric, Optimization & Components)

Цель: сделать оценку конфигурируемой под задачу, добавить MetricOps/HITL контур и углубить оптимизацию.

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
3. После каждого слайса сразу обновляем:
   - `Roadmap.md`
   - `README.md`
   - `System_Architecture_Overview.md` (если менялась архитектура)
   - `docs/adr/*` (если было архитектурное решение)
4. Каждый слайс фиксируется отдельным commit.
5. Перед commit обязателен полный прогон `python -m pytest` (unit + integration + e2e).

## Backlog Source

Детализированный исполнимый backlog:

- [docs/backlog/Executable_Slice_Backlog.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)

## Demo Track

Синхронный демо-трек проекта:

- [docs/demo/Demo_Track.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)
