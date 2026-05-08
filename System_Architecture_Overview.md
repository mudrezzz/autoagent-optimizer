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

## High-Level Layers

```text
Input (Task + Constraints + Data + Tools + Budget)
  -> Architecture Generator
  -> AgentOpt DSL
  -> Graph IR (runtime-neutral)
  -> Renderer (LangGraph first)
  -> Execution Runtime
  -> White-box Trace + Metrics
  -> Evaluation Fabric (configurable evaluators + metrics)
  -> Tournament + Optimization
  -> Evidence Pack + Champion Export
```

## Current Target Architecture (MVP-1)

1. `DSL Layer`
   - YAML-first spec.
   - Typed validation.
2. `Graph IR Layer`
   - Runtime-neutral graph model.
   - Explicit node contracts.
3. `Renderer Layer`
   - IR -> `BaseWorkflow`/`WorkflowNodeSpec` adapter over `langgraph-dai`.
4. `Execution Layer`
   - invoke/resume path.
   - fallback-safe execution mode.
5. `Evaluation Layer`
   - task-specific `Evaluation Profile` (config-driven metrics, judges, gates).
   - pluggable evaluator adapters:
     - golden dataset oracle,
     - LLM-as-judge,
     - executable validator (tests/code/run),
     - render validator.
   - Metric-Crafting Agent loop with HITL approval for metric/profile evolution.
6. `Optimization Layer`
   - equal-budget baseline tournament.
   - dual-metrics model:
     - comparative metrics for ranking,
     - diagnostic signals for bottleneck localization.
   - local config search in promoted families.
7. `Evidence Layer`
   - champion/challenger comparison.
   - reproducible artifact bundle.
   - native standalone export package on `langgraph-dai`.

## External Dependency Strategy

`langgraph-document-ai-platform` используется как внешний framework reference и library dependency.

- Integration mode: `Install as a Library` (`langgraph-dai` package).
- Version policy: pin to explicit tag for reproducibility.
- Coupling rule: избегаем прямой зависимости на нестабильные internal API через adapter boundary в нашем коде.
- Export rule: winner runtime artifact не должен зависеть от `optimizer.*` в production запуске.

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
2. Next:
   - Native export independence track (`I4.S4`-`I4.S8`),
   - Evaluation Fabric & MetricOps (`I5.*`) после закрытия native export track.

## Decision Records

Архитектурные решения фиксируются в:

- [docs/adr/README.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)

Изменение архитектурного направления без ADR не допускается.
