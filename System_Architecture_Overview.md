# System Architecture Overview

## Purpose

`AutoAgent Optimizer` - control plane для поиска и оптимизации архитектур compound AI systems.

Ключевой runtime target на MVP: LangGraph через библиотечную интеграцию `langgraph-dai`.

## Architectural Principles

1. OSS-first composability.
2. Control plane over existing runtimes (not a replacement).
3. White-box observability at node/edge level.
4. Contract-first components.
5. Human-in-the-loop at decision checkpoints.
6. Budget-aware optimization.
7. Runtime artifact independence from control plane.
8. Frontend architecture is `React + TypeScript`, capability-driven, with UX North Star based on `design_system/screenshots/app-v3.png`.

## High-Level Layers

```text
Input (Tenant + User + Battle + Task Brief + Constraints + Data + Budget)
  -> Product Experience Layer (Battles Hub / Battle Workspace)
  -> Copilot Orchestrator (task-to-candidates loop)
  -> Pattern Library + RAG Retrieval
  -> Architecture Generator
  -> Internal Agent Spec -> AgentOpt DSL
  -> Graph IR (runtime-neutral)
  -> Renderer (LangGraph first)
  -> Execution Runtime
  -> White-box Trace + Metrics
  -> Dataset + Evaluator Fabric
  -> Evaluation Fabric (configurable evaluators + metrics)
  -> Tournament + Optimization
  -> Evidence Pack + Champion Export/Import
```

## Current Target Architecture (MVP-2 transition)

1. `Battle Registry Layer`
   - tenant-scoped battle registry   .
   -    (agents/datasets/metrics/prompts/tools/settings).
2. `Copilot Layer`
   - Chat-first  .
   - Candidate generation +   .
3. `Pattern Layer`
   -  design patterns.
   - RAG retrieval      prompt context.
4. `DSL Layer (internal)`
   - DSL    UI.
   - Typed validation/compile   readiness gate.
5. `Graph IR Layer`
   - Runtime-neutral graph model.
   - Explicit node contracts.
6. `Renderer Layer`
   - IR -> `BaseWorkflow`/`WorkflowNodeSpec` adapter over `langgraph-dai`.
7. `Execution Layer`
   - invoke/resume path.
   - fallback-safe execution mode.
8. `Evaluation Layer`
   - dataset lifecycle (upload/manual/synthetic/clean/check).
   - task-specific `Evaluation Profile` (config-driven metrics, judges, gates).
   - pluggable evaluator adapters:
     - golden dataset oracle,
     - LLM-as-judge,
     - executable validator (tests/code/run),
     - render validator.
   - Metric-Crafting Agent loop with HITL approval for metric/profile evolution.
9. `Optimization Layer`
   - equal-budget baseline tournament.
   - dual-metrics model:
     - comparative metrics for ranking,
     - diagnostic signals for bottleneck localization.
   - local config search in promoted families.
10. `Evidence Layer`
   - champion/challenger comparison.
   - reproducible artifact bundle.
   - native standalone export package on `langgraph-dai`.
   - native import path for re-benchmark after external code changes.
   - post-export benchmark loop (native artifact re-evaluation + regression gates).
11. `Product Experience Layer`
   - capability-oriented frontend surfaces (`battles-hub` + `battle-workspace`).
   - unified scenario runner for demo/validation.
   - explicit mapping `backend capability -> user-visible control -> e2e assertion`.
   - risk-based QA gates for delivery speed (`fast` / `targeted` / `full`) with full regression reserved for high-risk slices.
   - strict `design_system` compliance (tokens, typography, iconography, UI kits, voice).
   - docs-as-code wiki in current repository (`docs/wiki`) published via GitHub Pages and updated per vertical slice.
   - UX composition rule: `Battles Hub` без правого rail; `Battle Workspace` по North Star (`app-v3`).

## External Dependency Strategy

`langgraph-document-ai-platform` используется как внешний framework reference и library dependency.

- Integration mode: `Install as a Library` (`langgraph-dai` package).
- Version policy: pin to explicit tag for reproducibility.
- Coupling rule: избегаем прямой зависимости на нестабильные internal API через adapter boundary в нашем коде.
- Export rule: winner runtime artifact не должен зависеть от `optimizer.*` в production запуске.
- Frontend rule: UI implementation must follow local `design_system` package as single source of truth.
- Frontend architecture rule: follow [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md) for structure/state/contracts and North Star UX.

## Core Internal Modules (Planned)

1. `optimizer.dsl`
2. `optimizer.graph_ir`
3. `optimizer.renderer.langgraph_dai`
4. `optimizer.codegen`
5. `optimizer.arena`
6. `optimizer.evaluation`
7. `optimizer.metricops` (planned)
8. `optimizer.components`
9. `optimizer.evidence`
10. `optimizer.champion`
11. `frontend` (planned capability UI layer C1..C6)
12. `optimizer.workspace`
13. `optimizer.copilot` (planned)
14. `optimizer.patterns` (planned)
15. `optimizer.versioning` (planned)
16. `optimizer.native_import` (planned)

## Missing Elements (Frontend + Backend)

-:

1.  `Project Chat`     ;
2.  pattern library browser  include/exclude controls;
3.  dataset/metrics/evaluator studio;
4.  run-monitor    version-manifest;
5.  native import UX path.

-:

1.  copilot orchestrator (task brief -> candidate set);
2.  pattern library RAG service;
4.  unified version-manifest service;
5.  dataset synthesis/cleaning assistant pipeline;
6.  native import parser + compatibility pipeline.

## Implementation Status Snapshot

1. Implemented:
   - `optimizer.dsl.schema` (typed DSL v0),
   - `optimizer.dsl.io` (YAML loading + validation),
   - `optimizer.dsl.validate` (CLI smoke validation),
   - `examples/dsl/*` (3 базовых сценария),
   - `optimizer.graph_ir.models` (typed Graph IR v0),
   - `optimizer.graph_ir.validators` (start/end/edge/reachability checks),
   - `optimizer.graph_ir.validate` (CLI smoke validation),
   - `examples/graph_ir/*` (3 референсных Graph IR сценария),
   - `optimizer.dsl.compiler` (DSL -> Graph IR compile),
   - `optimizer.dsl.compile_report` (node mapping + issues),
   - `optimizer.dsl.compile` (CLI compile path),
   - `optimizer.renderer.langgraph_dai.workflow` (исполняемый runtime workflow),
   - `optimizer.renderer.langgraph_dai.adapter` (IR -> BaseWorkflow adapter),
   - `optimizer.renderer.langgraph_dai.run` (CLI runtime execution),
   - `optimizer.codegen.agent_generator` (Graph IR -> generated runnable package),
   - `optimizer.codegen.generate` (CLI code generation path),
   - `optimizer.tracing.node_events` (structured node-level events),
   - `optimizer.tracing.trace_store` (in-memory trace summary per run),
   - `optimizer.renderer.langgraph_dai.checkpoint_store` (invoke/resume checkpoint contract),
   - `optimizer.evaluation.dataset_schema` (golden dataset typed contract),
   - `optimizer.evaluation.dataset_loader` (JSONL loader with line diagnostics),
   - `optimizer.evaluation.validate_dataset` (CLI dataset validation),
   - `optimizer.evaluation.oracle_rules` (v0 правила `must_include/forbidden`),
   - `optimizer.evaluation.oracle_runner` (исполняемый runner и summary),
   - `optimizer.evaluation.run_oracle` (CLI oracle прогона),
   - `Evaluation Profile` design direction (task-specific metrics/evaluator contracts),
   - `optimizer.evaluation.profile_schema` (typed evaluation profile contract v0),
   - `optimizer.evaluation.profile_io` (YAML loading + validation for profile),
   - `optimizer.evaluation.profile_runner` (profile orchestration for `dsl_runtime`/`native_runtime`),
   - `optimizer.evaluation.native_compatibility` (native target preflight compatibility report + strict blocking),
   - `optimizer.evaluation.run_profile` (CLI profile-driven run path),
   - `optimizer.arena.tournament_schema` (typed contract config-driven `budget`/`ranking`/`evaluator` policies),
   - `optimizer.arena.runner` (config-driven tournament execution и ranking),
   - `optimizer.arena.run_tournament` (CLI tournament compare path),
   - `optimizer.metrics.middle_metrics` (middle-метрики и latency/cost агрегаты),
   - `optimizer.arena` scoring path (`composite_score`, `score_breakdown`, config-driven weights),
   - `optimizer.metrics.diagnostic_signals` (stage-level diagnostic signals и bottleneck score),
   - `optimizer.arena` dual output contract (`comparison` + `diagnostics`).
   - stylizer demo dataset v1 expanded to multi-case full profile (`examples/datasets/golden_linkedin_stylizer_v1.jsonl`),
   - arena budget profiles (`smoke`/`full`) via dedicated configs (`support_tournament*_v0.yaml`),
   - arena run-policy split (`smoke-live` vs `decision-live`) for cheap signal vs architecture decision confidence,
   - economical live-default OpenRouter model profile for demo loops (`meta-llama/llama-3.1-8b-instruct`).
   - `optimizer.evidence` (Evidence Pack v0 JSON/Markdown artifacts with winner/challenger explainable diff),
   - `optimizer.champion` (Champion Export Bundle v0: arena/evidence/diagnostic/codegen bundle + manifest).
   - `optimizer.champion.native_export` (standalone `langgraph-dai` native runtime export v0).
   - `optimizer.workspace` (JSON-backed battle/arena registry store with tenant/user-scoped C1 access),
   - `optimizer.frontend.dev_server` + `frontend/` (V2.3.S1 + V2.3.S1a + V2.3.S2 + V2.3.S2b + V2.3.S2c + V2.3.S5a + V2.3.S6 + V2.3.S6a + V2.3.S7: C1 registry + C2 battle-chat/candidate surfaces + C4 dataset/evaluation studios + C5 optimizer setup/guardrails + sticky shell + unit/integration/e2e smoke coverage),
   - `optimizer.c2` (deterministic brief-to-candidates generator + arena-scoped chat state contract + compile-readiness gate with per-candidate reports).
   - C3 pattern library UI/selection with saved include set and retrieval trace.
   - C4 dataset studio v0 (dataset create/select, row add/replace, validate, version snapshot) via `/api/arenas/{id}/datasets/*`.
   - C4 UX unification layer: candidate-like dataset list, multi-dataset assignment (`/datasets/assign`) and dedicated dataset editor screen with breadcrumbs.
   - C4 metrics & evaluators studio v0 (comparative/diagnostic metrics, evaluator adapters, budget limits, validate/version flow) via `/api/arenas/{id}/evaluation/*`.
   - C4 corrective UX split: explicit `Datasets`/`Metrics` tabs with isolated user flows and regression tests.
   - C5 optimizer setup studio v0 (methods/controls/run-plan/budget, preflight guardrails, profile versioning, launch queue) via `/api/arenas/{id}/optimizer/*`.
2. Next:
   - Vertical product delivery track (`V2.3.*`) moves to C5 run-monitor timeline after C5 setup/launch guardrails slice completion.
   - Evaluation Fabric & MetricOps (`I5.*`) including evaluator adapter layer and post-export native evaluation loop.

## Decision Records

Архитектурные решения фиксируются в:

- [docs/adr/README.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)

зменение архитектурного направления без ADR не допускается.


