# Executable Slice Backlog

## Purpose

Этот документ переводит ТЗ в исполнимые слайсы с явными критериями приемки, зависимостями и порядком реализации.

## Prioritization Policy

1. Сначала закрываем сквозной путь MVP-1 (`DSL -> IR -> Render -> Run -> Evaluate -> Evidence`).
2. Приоритет у слайсов, которые:
   - снижают архитектурный риск;
   - дают проверяемый end-to-end прогресс;
   - разблокируют несколько следующих слайсов.
3. В каждом активном окне детально планируются только ближайшие 1-2 итерации.

## Active Window (Now)

- `Current Focus`: MVP-1 / I1-I2
- `Active Next Slice`: I2.S3

---

## Detailed Backlog: I1-I2

### I1.S1 - DSL v0 schema draft (YAML-first)

- Status: Done
- Goal: зафиксировать минимальный язык описания проекта/архитектуры для дальнейшей компиляции.
- Inputs: FR-4, FR-1/2/3 из ТЗ.
- Deliverables:
  - `optimizer/dsl/schema.py` (typed contracts),
  - `examples/dsl/*.yaml`,
  - `docs/specs/DSL_v0.md`.
- Acceptance Criteria:
  1. Валидируется минимум 3 сценария: `direct_llm`, `ocr_first`, `hitl_gate`.
  2. Ошибки валидации человекочитаемые и указывают путь до поля.
  3. Есть smoke-check команда для DSL validation.
- Dependencies: none.
- Risks: переусложнение DSL до подтверждения базового рендера.

### I1.S2 - Graph IR v0 typed model

- Status: Done
- Goal: runtime-neutral представление графа, независимое от конкретного runtime.
- Inputs: FR-5, FR-6.
- Deliverables:
  - `optimizer/graph_ir/models.py`,
  - `optimizer/graph_ir/validators.py`,
  - `docs/specs/GraphIR_v0.md`.
- Acceptance Criteria:
  1. IR покрывает node types: `llm`, `deterministic`, `tool`, `validator`, `hitl_gate`.
  2. Есть edge-валидация, включая start/end и unreachable nodes.
  3. Есть сериализация/десериализация без потери структуры.
- Dependencies: I1.S1.
- Risks: протекание runtime-специфичных полей в IR.

### I1.S3 - DSL -> IR compiler v0

- Status: Done
- Goal: компиляция DSL в Graph IR с отчетом о трансформации.
- Inputs: FR-4, FR-5.
- Deliverables:
  - `optimizer/dsl/compiler.py`,
  - `optimizer/dsl/compile_report.py`.
- Acceptance Criteria:
  1. Любой валидный DSL из examples компилируется в валидный IR.
  2. Отчет компиляции содержит warnings/errors и node mapping.
  3. Есть regression tests на compile success/failure.
- Dependencies: I1.S1, I1.S2.
- Risks: неявная магия в compiler; решается explicit mapping rules.

### I2.S1 - LangGraph renderer adapter on top of langgraph-dai

- Status: Done
- Goal: превратить IR в исполняемый workflow через `BaseWorkflow`.
- Inputs: FR-6, ADR-0001.
- Deliverables:
  - `optimizer/renderer/langgraph_dai/adapter.py`,
  - `optimizer/renderer/langgraph_dai/workflow_builder.py`,
  - renderer smoke script.
- Acceptance Criteria:
  1. IR рендерится в workflow и выполняется `invoke`.
  2. Поддерживается минимум linear flow + one conditional branch.
  3. Adapter изолирует внешнюю библиотеку в отдельном модуле.
- Dependencies: I1.S2, I1.S3.
- Risks: зависимость от internal API внешней библиотеки.

### I2.S2 - Agent code generation v0

- Status: Done
- Goal: получить materialized Python-артефакт агента из лучшей DSL/IR конфигурации.
- Inputs: FR-6, runtime path I2.S1.
- Deliverables:
  - `optimizer/codegen/agent_generator.py`,
  - `optimizer/codegen/generate.py`,
  - `docs/specs/Agent_Codegen_v0.md`.
- Acceptance Criteria:
  1. Есть CLI генерации из DSL или Graph IR.
  2. Генератор создает runnable package + runner script.
  3. Есть smoke-путь `DSL -> generate code -> run generated agent`.
- Dependencies: I1.S3, I2.S1.
- Risks: fallback-логика может скрыть отсутствие production-обработчиков, поэтому нужны явные TODO в артефакте.

### I2.S3 - Node event capture + white-box trace v0

- Status: Planned
- Goal: снять node-level события и сделать базовый trace storage format.
- Inputs: FR-9, FR-10.
- Deliverables:
  - `optimizer/tracing/node_events.py`,
  - `optimizer/tracing/trace_store.py`,
  - `docs/specs/Whitebox_Trace_v0.md`.
- Acceptance Criteria:
  1. Для каждого node фиксируются `started/completed/failed`.
  2. Trace привязан к run_id/task_id.
  3. Можно получить summary по run (node count, failures, duration).
- Dependencies: I2.S1.
- Risks: разрыв между runtime events и evaluation metrics.

### I2.S4 - Resume/checkpoint contract path

- Status: Planned
- Goal: подтвержденный invoke/resume сценарий для долгих execution.
- Inputs: FR-6, FR-19.
- Deliverables:
  - resume state contract tests,
  - checkpoint integration smoke.
- Acceptance Criteria:
  1. interrupt/resume проходит без потери state.
  2. task/thread id консистентно переносится в runtime.
  3. Есть negative tests для missing/invalid task_id.
- Dependencies: I2.S1.
- Risks: неконсистентность state-модели между invoke и resume.

---

## Detailed Backlog: I3-I4 (Ready For Detailing Later)

- I3.S1 dataset JSONL loader
- I3.S2 executable oracle runner
- I3.S3 equal-budget arena
- I4.S1 middle metrics v0
- I4.S2 evidence pack generator
- I4.S3 champion export bundle

Детальные acceptance criteria уточняются после завершения I2.

---

## Done Slices

### I0.S1 - Done

- Governance baseline docs + ADR process.
- Commit: `9579344`.

### I0.S2 - Done

- Создан этот executable backlog и синхронизированы статусные документы.
- Commit: tracked in git history.

### I0.S3 - Done

- Добавлен синхронный demo track и зафиксирована политика его обязательного развития.
- Принят ADR с обязательным demo-sync правилом.
- Commit: tracked in git history.

### I1.S1 - Done

- Реализованы typed DSL v0 schema, YAML loader, CLI-валидатор и smoke-скрипт.
- Добавлены 3 валидных референсных спецификации: `direct_llm`, `ocr_first`, `hitl_gate`.
- Commit: tracked in git history.

### I1.S2 - Done

- Реализованы runtime-neutral Graph IR models + validators + CLI.
- Добавлены edge/start/end/unreachable проверки и roundtrip сериализация.
- Добавлены unit/integration/e2e тесты для Graph IR и smoke-скрипт.
- Commit: tracked in git history.

### I1.S3 - Done

- Реализован компилятор DSL -> Graph IR с compile report.
- Добавлены CLI компиляции и smoke-скрипт сквозной компиляции DSL-примеров.
- Добавлены unit/integration/e2e тесты на success/failure compile path.
- Commit: tracked in git history.

### I2.S1 - Done

- Реализован runtime renderer Graph IR -> BaseWorkflow (langgraph-dai).
- Добавлен runtime CLI и smoke demo запуск workflow.
- Добавлены unit/integration/e2e тесты рендерера и branch-логики.
- Commit: tracked in git history.

### I2.S2 - Done

- Реализован codegen-путь DSL/IR -> runnable Python package агента.
- Добавлен CLI генерации `python -m optimizer.codegen.generate`.
- Добавлен smoke demo генерации и запуска сгенерированного агента.
- Добавлены unit/integration/e2e тесты нового функционала.
- Commit: tracked in git history.
