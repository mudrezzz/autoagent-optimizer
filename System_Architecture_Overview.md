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

## High-Level Layers

```text
Input (Task + Constraints + Data + Tools + Budget)
  -> Architecture Generator
  -> AgentOpt DSL
  -> Graph IR (runtime-neutral)
  -> Renderer (LangGraph first)
  -> Execution Runtime
  -> White-box Trace + Metrics
  -> Evaluation + Tournament + Optimization
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
   - deterministic oracles first (schema/pytest).
   - optional LLM-as-judge as auxiliary signal.
6. `Optimization Layer`
   - equal-budget baseline tournament.
   - local config search in promoted families.
7. `Evidence Layer`
   - champion/challenger comparison.
   - reproducible artifact bundle.

## External Dependency Strategy

`langgraph-document-ai-platform` используется как внешний framework reference и library dependency.

- Integration mode: `Install as a Library` (`langgraph-dai` package).
- Version policy: pin to explicit tag for reproducibility.
- Coupling rule: избегаем прямой зависимости на нестабильные internal API через adapter boundary в нашем коде.

## Core Internal Modules (Planned)

1. `optimizer.dsl`
2. `optimizer.graph_ir`
3. `optimizer.renderer.langgraph_dai`
4. `optimizer.codegen`
5. `optimizer.arena`
6. `optimizer.evaluation`
7. `optimizer.components`
8. `optimizer.evidence`

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
   - `optimizer.evaluation.run_oracle` (CLI oracle прогона).
2. Next:
   - Architecture Arena equal-budget tournament v0 (I3.S3).

## Decision Records

Архитектурные решения фиксируются в:

- [docs/adr/README.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)

Изменение архитектурного направления без ADR не допускается.
