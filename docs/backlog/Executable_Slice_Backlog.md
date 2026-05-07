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

- `Current Focus`: MVP-1 / I4
- `Active Next Slice`: I4.S2

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

- Status: Done
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

- Status: Done
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

## Detailed Backlog: I3-I4

### I3.S1 - Golden dataset JSONL + loader

- Status: Done
- Goal: зафиксировать единый dataset-контракт и загрузчик для evaluation-итераций.
- Inputs: FR-7, FR-8 (подготовка к oracle/arena).
- Deliverables:
  - `optimizer/evaluation/dataset_schema.py`,
  - `optimizer/evaluation/dataset_loader.py`,
  - `optimizer/evaluation/validate_dataset.py`,
  - `examples/datasets/golden_support_v1.jsonl`.
- Acceptance Criteria:
  1. Валидный JSONL датасет загружается без ошибок.
  2. Невалидные строки дают понятную ошибку с номером строки.
  3. CLI валидации возвращает summary и корректный exit code.
- Dependencies: I2.S4.
- Risks: недоопределенный `expected` контракт для сложных доменных задач (будет уточнен в I3.S2).

### I3.S2 - Executable oracle runner (schema/pytest)

- Status: Done
- Goal: исполняемая oracle-проверка результата по `expected` контракту датасета.
- Deliverables:
  - `optimizer/evaluation/oracle_rules.py`,
  - `optimizer/evaluation/oracle_runner.py`,
  - `optimizer/evaluation/run_oracle.py`,
  - `scripts/smoke_run_oracle.ps1`,
  - `docs/specs/Oracle_Runner_v0.md`.
- Acceptance Criteria:
  1. Есть rule-contract v0 (`must_include`/`forbidden`) и pass/fail по каждому кейсу.
  2. CLI выдает summary (`cases_total/passed/failed/pass_rate`) и корректный exit code.
  3. Есть deterministic `expected_stub` режим для smoke/CI.
  4. Добавлены unit/integration/e2e тесты и зеленый полный `python -m pytest`.
- Dependencies: I3.S1.
- Risks: правила v0 текстовые и не покрывают семантическую эквивалентность ответов.

### I3.S3 - Architecture Arena equal-budget tournament v0

- Status: Done
- Goal: сравнение 2-3 архитектур в равном бюджете с reproducible отчетом.
- Deliverables:
  - `optimizer/arena/tournament_schema.py`,
  - `optimizer/arena/io.py`,
  - `optimizer/arena/runner.py`,
  - `optimizer/arena/run_tournament.py`,
  - `examples/arena/support_tournament_v0.yaml`,
  - `scripts/smoke_run_arena.ps1`,
  - `docs/specs/Architecture_Arena_v0.md`.
- Acceptance Criteria:
  1. Один CLI-запуск сравнивает минимум 2 и максимум 3 архитектуры на общем датасете.
  2. Equal-budget policy (`equal_cases`) применяет одинаковый набор кейсов для всех участников.
  3. Отчет содержит ranking и winner по прозрачным правилам tie-break.
  4. Добавлены unit/integration/e2e тесты и зеленый полный `python -m pytest`.
- Dependencies: I3.S2.
- Risks: `expected_stub` режим дает упрощенный baseline и не заменяет production runtime-сравнение.

### I4.S1 - Middle-metrics v0

- Status: Done
- Goal: ввести промежуточные метрики качества/стоимости/латентности.

### I4.S2 - Evidence pack generator

- Status: In Progress
- Goal: собрать evidence pack champion/challenger с разделением comparative и diagnostic метрик.
- Deliverables:
  - `optimizer/evidence/*` (генератор отчетов),
  - `docs/specs/Evidence_Pack_v0.md`,
  - обновленный JSON-контракт результатов Arena (`comparison` + `diagnostics` разделы).
- Acceptance Criteria:
  1. В отчете отдельные секции:
     - `comparison` (для ranking),
     - `diagnostics` (для локализации bottleneck).
  2. Для каждого candidate есть минимум:
     - `comparative_metrics`,
     - `diagnostic_signals_by_stage`.
  3. Для winner/challenger формируется explainable diff по comparative-метрикам.
  4. Добавлены unit/integration/e2e тесты и зеленый полный `python -m pytest`.
- Dependencies: I4.S1.
- Risks: смешение ranking-метрик и root-cause сигналов в одной шкале.
- Progress (2026-05-07):
  1. Введен dual output контракт в arena JSON: `comparison` + `diagnostics`.
  2. Добавлены базовые stage-level diagnostic signals с `bottleneck_score`.

### I4.S3 - Champion export bundle

- Status: Planned
- Goal: сформировать экспортируемый пакет лучшей конфигурации и диагностической карты улучшений.
- Deliverables:
  - bundle champion artifacts,
  - `diagnostic_map.json` (top bottlenecks + suggested interventions).
- Acceptance Criteria:
  1. Bundle включает runnable config/code и evidence pack.
  2. Диагностическая карта содержит приоритизированные точки оптимизации.
  3. Добавлены integration/e2e проверки экспортируемого комплекта.
- Dependencies: I4.S2.
- Risks: переизбыточный объем bundle без явной структуры.

---

## Detailed Backlog: I5-I7

### I5.S1 - Task Evaluation Profile v0

- Status: Planned
- Goal: ввести config-driven профиль оценки под каждый task type.
- Deliverables:
  - `docs/specs/Evaluation_Profile_v0.md`,
  - typed profile schema + validator (`optimizer/evaluation/profile_*`),
  - examples профилей для минимум 2 task types.
- Acceptance Criteria:
  1. Можно задать разные comparative/diagnostic метрики для разных задач.
  2. Можно задать разные evaluator chains без code changes.
  3. Есть валидация profile contract и понятные ошибки.
- Dependencies: I4.S2.
- Risks: избыточная сложность профиля на v0.

### I5.S2 - Evaluator Adapter Layer v0

- Status: Planned
- Goal: подключать разные методы оценки через единый adapter contract.
- Deliverables:
  - evaluator adapter interface,
  - базовые adapters:
    - golden_oracle,
    - llm_judge,
    - executable,
    - render,
  - aggregation pipeline profile-driven метрик.
- Acceptance Criteria:
  1. Один и тот же турнир может использовать разные evaluator compositions.
  2. Для evaluator можно задавать budget/limits в profile.
  3. Есть integration tests на mixed evaluator pipeline.
- Dependencies: I5.S1.
- Risks: несогласованность шкал между evaluator types.

### I5.S3 - Metric-Crafting Agent + HITL loop v0

- Status: Planned
- Goal: сделать настройку/эволюцию метрик агентной задачей с human approval.
- Deliverables:
  - metric-crafting workflow (draft -> critique -> approve),
  - HITL checkpoint contract для profile activation,
  - change log профилей метрик.
- Acceptance Criteria:
  1. Агент может предложить profile draft для нового кейса.
  2. Без HITL approve профиль не активируется для ranking.
  3. Есть audit trail: кто/когда/почему изменил профиль.
- Dependencies: I5.S1, I5.S2.
- Risks: высокая вариативность качества auto-generated метрик.

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

### I2.S3 - Done

- Реализован white-box trace v0 с node-level событиями `started/completed/failed/skipped`.
- Добавлен `InMemoryTraceStore` и агрегированная `trace_summary` по run/task.
- Runtime и CLI теперь возвращают `node_events` + `trace_summary`.
- Добавлены unit/integration тесты trace-контракта.
- Commit: tracked in git history.

### I2.S4 - Done

- Реализован checkpoint/resume контракт с файловым checkpoint-store.
- Добавлен invoke/resume путь в runtime API и CLI (`--resume-task-id`, `--checkpoint-dir`).
- Добавлены integration/negative тесты на missing/invalid task_id.
- Добавлен smoke invoke->resume сценарий в runtime demo.
- Commit: tracked in git history.

### I3.S1 - Done

- Введен Golden Dataset JSONL контракт (`case_id`, `input`, `expected`, `tags`, `metadata`).
- Реализован typed loader с диагностикой ошибок по line number.
- Добавлен CLI `python -m optimizer.evaluation.validate_dataset`.
- Добавлен smoke-скрипт валидации датасета и покрытие unit/integration/e2e.
- Commit: tracked in git history.

### I3.S2 - Done

- Реализован executable oracle runner на базе `must_include/forbidden` правил.
- Добавлен CLI `python -m optimizer.evaluation.run_oracle` и smoke-скрипт oracle прогона.
- Добавлены deterministic (`expected_stub`) и runtime пути исполнения.
- Добавлены unit/integration/e2e тесты и зеленый full pytest gate.
- Commit: tracked in git history.

### I3.S3 - Done

- Реализован Architecture Arena v0 для сравнения 2-3 архитектур.
- Введен equal-budget policy `equal_cases` с единым набором кейсов для всех участников.
- Добавлен CLI `python -m optimizer.arena.run_tournament`, example tournament config и smoke-скрипт.
- Добавлены unit/integration/e2e тесты arena-контура.
- Commit: tracked in git history.
