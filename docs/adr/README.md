# ADR / ARD Index

Этот каталог хранит архитектурные решения проекта.

Терминология:

- `ADR` (Architecture Decision Record) - базовый формат.
- `ARD` - допустимое внутреннее синонимичное название в проекте.

## Rules

1. Любое существенное архитектурное решение фиксируется отдельным ADR.
2. ADR создается до реализации или в том же слайсе, где решение внедрено.
3. ADR не переписывается задним числом; изменения оформляются новым ADR (supersedes).
4. Каждый ADR связан со слайсом roadmap (`I*.S*`) и commit hash.

## Status Values

- `Proposed`
- `Accepted`
- `Superseded`
- `Deprecated`

## File Naming

`ADR-XXXX-short-title.md`, где `XXXX` - четырехзначный номер.

## ADR List

1. [ADR-0001-use-langgraph-dai-as-render-target.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0001-use-langgraph-dai-as-render-target.md) - Accepted
2. [ADR-0002-dsl-v0-yaml-first.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0002-dsl-v0-yaml-first.md) - Accepted
3. [ADR-0003-mandatory-test-pyramid-and-full-gate.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0003-mandatory-test-pyramid-and-full-gate.md) - Accepted
4. [ADR-0004-graph-ir-v0-runtime-neutral-boundary.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0004-graph-ir-v0-runtime-neutral-boundary.md) - Accepted
5. [ADR-0005-continuous-demo-track-policy.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0005-continuous-demo-track-policy.md) - Accepted
6. [ADR-0006-dsl-to-graph-ir-mapping-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0006-dsl-to-graph-ir-mapping-v0.md) - Accepted
7. [ADR-0007-render-graph-ir-via-langgraph-dai-workflow.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0007-render-graph-ir-via-langgraph-dai-workflow.md) - Accepted
8. [ADR-0008-add-agent-code-generation-path.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0008-add-agent-code-generation-path.md) - Accepted
9. [ADR-0009-node-event-capture-and-trace-summary-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0009-node-event-capture-and-trace-summary-v0.md) - Accepted
10. [ADR-0010-resume-checkpoint-contract-path-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0010-resume-checkpoint-contract-path-v0.md) - Accepted
11. [ADR-0011-golden-dataset-jsonl-contract-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0011-golden-dataset-jsonl-contract-v0.md) - Accepted
12. [ADR-0012-executable-oracle-runner-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0012-executable-oracle-runner-v0.md) - Accepted
13. [ADR-0013-architecture-arena-equal-budget-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0013-architecture-arena-equal-budget-v0.md) - Accepted
14. [ADR-0014-arena-policies-config-driven.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0014-arena-policies-config-driven.md) - Accepted
15. [ADR-0015-middle-metrics-and-composite-scoring-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0015-middle-metrics-and-composite-scoring-v0.md) - Accepted
16. [ADR-0016-dual-metrics-model-comparative-vs-diagnostic.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0016-dual-metrics-model-comparative-vs-diagnostic.md) - Accepted
17. [ADR-0017-evidence-pack-dual-output-contract-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0017-evidence-pack-dual-output-contract-v0.md) - Accepted
18. [ADR-0018-champion-export-bundle-v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0018-champion-export-bundle-v0.md) - Accepted
19. [ADR-0019-native-langgraph-dai-export-without-optimizer-runtime.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0019-native-langgraph-dai-export-without-optimizer-runtime.md) - Accepted
20. [ADR-0020-native-exporter-minimal-v0-and-fallback-policy.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0020-native-exporter-minimal-v0-and-fallback-policy.md) - Accepted

## Template

Использовать:

- [ADR-TEMPLATE.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-TEMPLATE.md)
