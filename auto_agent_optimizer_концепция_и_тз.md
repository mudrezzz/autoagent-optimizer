# AutoAgent Optimizer

## Единая концепция и техническое задание

**Версия:** 0.1  
**Статус:** концепция / product & technical specification draft  
**Позиционирование:** OSS-first white-box optimization platform for compound AI systems

---

# 1. Executive Summary

**AutoAgent Optimizer** — это OSS-first платформа для автоматического проектирования, сравнения, диагностики и оптимизации AI-agentic решений и более широких **compound AI systems**.

Система принимает описание задачи, ограничения, доступные модели, tools, knowledge sources, APIs, MCP-сервера, datasets и бюджет экспериментов. Затем она генерирует несколько архитектурно разных baseline-решений, рендерит их в исполняемые workflow, например на LangGraph, прогоняет их на golden datasets, собирает white-box traces, считает output-метрики и middle-метрики, диагностирует слабые места, предлагает или применяет targeted interventions, сравнивает архитектурные семейства между собой и возвращает deployable champion configuration с доказательной базой.

Ключевая идея: зрелый AI-агент — это не просто набор вызовов LLM. Это исполняемый граф из LLM-ноды, deterministic code nodes, tools, validators, tests, MCP-серверов, retrieval components, policy gates, HITL-гейтов и runtime-политик.

AutoAgent Optimizer должен отвечать не только на вопрос:

> Какой prompt / model / RAG config лучше?

А на более сильный инженерный вопрос:

> Какая часть AI-системы должна быть LLM, какая — кодом, какая — MCP/tool-сервисом, какая — тестом или валидатором, и какая архитектура даёт лучший trade-off по качеству, стоимости, latency, стабильности, безопасности и суверенности?

---

# 2. Product Thesis

Современное построение AI-агентов перешло из стадии демонстраций в стадию инженерной оптимизации. Команды должны оценивать и улучшать:

- качество;
- стабильность;
- стоимость;
- latency;
- безопасность;
- explainability;
- controllability;
- data privacy;
- суверенность;
- maintainability;
- production readiness.

При этом для одной и той же задачи существует почти бесконечное пространство решений:

- разные архитектуры пайплайна;
- разные модели;
- разные prompts;
- разные RAG-стратегии;
- разные tool-use стратегии;
- разные validators;
- разные MCP-сервера;
- разные deterministic code components;
- разные HITL-гейты;
- разные retry/fallback policies;
- разные budget allocation strategies.

Сегодня большинство команд строит AI-агентов интуитивно: сделали pipeline, вручную посмотрели несколько примеров, решили, что “в целом работает”, и пошли дальше. При этом часто неизвестно:

- является ли выбранная архитектура хорошей;
- насколько она лучше альтернатив;
- где именно она ломается;
- что нужно оптимизировать в первую очередь;
- есть ли более дешёвое решение с сопоставимым качеством;
- какие части стоит вынести из LLM в deterministic code;
- какие проверки должны быть executable tests, а не LLM-as-judge.

**AutoAgent Optimizer** предлагает перейти от prompt hacking и ad hoc agent engineering к доказательному optimization workflow.

---

# 3. Core Product Definition

## 3.1. Краткое определение

**AutoAgent Optimizer** — это open-source control plane для проектирования, генерации, оптимизации и доказательного сравнения AI-agentic workflows и compound AI systems.

## 3.2. Более точное определение

AutoAgent Optimizer — это система, которая:

1. принимает задачу и ограничения;
2. строит или импортирует golden dataset;
3. генерирует несколько архитектурно разных baseline-решений;
4. позволяет человеку отредактировать и утвердить candidate architectures;
5. описывает решения через декларативный DSL;
6. рендерит DSL в исполняемые workflow, сначала в LangGraph;
7. умеет подключать существующий пользовательский код, API, MCP-сервера и библиотеки;
8. умеет при необходимости генерировать bounded deterministic components по контракту;
9. запускает equal-budget tournament между архитектурами;
10. оптимизирует конфиги внутри promising architecture families;
11. собирает white-box traces и middle-метрики;
12. диагностирует bottlenecks и failure modes;
13. предлагает targeted interventions;
14. выбирает champion / challengers на Pareto frontier;
15. экспортирует код, конфиг, тесты, отчёты и deployment artifacts.

## 3.3. Главная формула

```text
Task + Constraints + Data + Tools + Code Capabilities
  -> Architecture Candidates
  -> Capability Gap Detection
  -> Component Selection / Synthesis / User Supply
  -> Executable Graph Rendering
  -> White-box Evaluation
  -> Diagnostic Interventions
  -> Architecture + Config + Component Optimization
  -> Champion Compound AI System
```

---

# 4. What This Product Is Not

AutoAgent Optimizer **не является**:

1. новым фреймворком для ручного построения агентов вместо LangGraph, LlamaIndex, CrewAI или AutoGen;
2. новой observability-платформой вместо Phoenix, Langfuse или MLflow;
3. новой платформой разметки данных;
4. универсальной IDE;
5. заменой Cursor/Copilot/Codex-like tooling;
6. marketplace всех MCP-серверов;
7. low-code backend builder;
8. платформой data engineering общего назначения;
9. системой, которая бесконтрольно генерирует arbitrary code.

Правильная роль продукта:

> Optimization and orchestration control plane поверх существующей OSS-экосистемы.

Продукт должен писать или оборачивать код только в рамках bounded, typed, testable, sandboxed pipeline components, которые являются частью оптимизируемого AI-решения.

---

# 5. Основной объект оптимизации

## 5.1. Старое понимание

```text
AI agent = LLM calls + prompts + tools
```

## 5.2. Новое понимание

```text
Compound AI system = executable graph of:
  - LLM nodes
  - deterministic code nodes
  - retrieval nodes
  - tool nodes
  - MCP servers
  - validators
  - tests / executable oracles
  - data transformations
  - policy gates
  - human gates
  - runtime services
  - observability hooks
```

## 5.3. Следствие

Оптимизировать нужно не только LLM-параметры, а всю архитектуру исполняемого графа:

- структуру graph;
- типы nodes;
- выбор LLM vs deterministic code;
- выбор готового OSS-компонента vs пользовательского кода vs code synthesis;
- tool-use strategy;
- MCP topology;
- validation strategy;
- dataset strategy;
- human involvement strategy;
- deployment constraints.

---

# 6. Ключевые принципы продукта

## 6.1. OSS-first

Платформа должна максимально переиспользовать OSS-экосистему и не закрывать пользователя в proprietary runtime.

## 6.2. Control plane, not agent framework

Продукт не заменяет LangGraph, LlamaIndex, CrewAI, Phoenix, Langfuse, MLflow, DSPy, Ragas, Promptfoo и другие инструменты. Он связывает их в единый optimization workflow.

## 6.3. White-box, not black-box

Оценка должна выполняться не только на уровне `input -> output`, но и на уровне внутренних nodes, edges, loops, validators, tools, retrieval steps и code components.

## 6.4. Architecture search before local tuning

Сначала нужно сравнить архитектурно разные baseline-решения, затем углубляться в оптимизацию promising families.

## 6.5. Budget-aware optimization

Все эксперименты должны учитывать стоимость, latency, лимиты API, compute budget и время.

## 6.6. Human as co-architect

HITL — это не только разметка ответов. Человек участвует в проектировании архитектуры, ревью датасета, выборе метрик, pruning/promote решениях, approval generated code и финальном champion selection.

## 6.7. Contract-first component development

Новые deterministic components, validators, MCP servers и API wrappers создаются или подключаются через явный контракт: input schema, output schema, invariants, tests, permissions, observability и security boundaries.

## 6.8. User-supplied components are first-class citizens

Пользователь должен иметь возможность взять контракт, реализовать компонент в своей IDE, принести MCP server / API / библиотеку / проект, и подключить его к AutoAgent Optimizer как candidate implementation.

## 6.9. Executable tests over subjective judges where possible

Если качество можно проверить через deterministic test, schema validation, pytest, SQL constraint или integration test, это предпочтительнее LLM-as-judge.

---

# 7. Основные роли пользователей

## 7.1. AI Engineer

- проектирует agentic workflows;
- выбирает architecture candidates;
- смотрит traces;
- анализирует failure modes;
- работает с prompts, tools, retrievers, validators.

## 7.2. ML / Evaluation Engineer

- проектирует golden datasets;
- определяет metrics;
- следит за overfitting;
- настраивает optimization policies;
- проверяет statistical significance.

## 7.3. Platform Engineer

- подключает модели, gateways, vector stores, MCP servers, observability backends;
- отвечает за runtime, Kubernetes, secrets, policies, sandboxing.

## 7.4. Backend / Software Engineer

- реализует missing deterministic components;
- подключает API;
- пишет MCP servers;
- пишет pytest/integration tests;
- ревьюит generated code.

## 7.5. Domain Expert

- утверждает golden answers;
- проверяет synthetic cases;
- калибрует rubrics;
- принимает финальное решение по бизнес-качеству.

## 7.6. Security / Compliance Officer

- утверждает data policies;
- проверяет side effects;
- контролирует доступы MCP/tools;
- утверждает deployment в regulated environments.

---

# 8. Основные сценарии использования

## 8.1. Оптимизация support agent

Пользователь хочет построить customer support agent, который отвечает на вопросы по базе знаний, использует CRM tools, умеет создавать тикеты, но не может выполнять risky actions без approval.

Система генерирует:

- Direct LLM baseline;
- Basic RAG;
- RAG + verifier;
- ReAct tool agent;
- Plan-and-execute tool agent;
- Router pipeline;
- HITL action workflow.

Затем сравнивает их по task success, groundedness, tool correctness, cost, latency, refusal correctness и unauthorized action rate.

## 8.2. OCR сложных PDF → таблица БД

Пользователь хочет найти оптимальную архитектуру для извлечения данных из сложных PDF и записи в БД.

Система генерирует:

- Vision LLM end-to-end extraction;
- Text-layer extraction + deterministic parser;
- OCR-first pipeline;
- Hybrid deterministic extraction + LLM repair;
- MCP OCR service + DB writer;
- Human review for low-confidence rows.

Система также может создать component contracts для:

- PDF classifier;
- OCR node;
- table extraction node;
- schema normalizer;
- DB validator;
- pytest oracle;
- MCP OCR server.

Пользователь может принять generated component или самостоятельно реализовать MCP/API по контракту.

## 8.3. Coding agent

Пользователь хочет оптимизировать агента, который пишет код.

Ключевой evaluator — не LLM judge, а executable tests:

- pytest;
- mypy;
- ruff;
- semgrep;
- integration tests;
- benchmark tests.

LLM используется для generation, planning, explanation и repair, но quality oracle — deterministic.

## 8.4. Enterprise document QA

Система сравнивает разные RAG architectures:

- flat RAG;
- hybrid search;
- reranker;
- hierarchical RAG;
- citation verifier;
- answer verifier;
- context compression;
- query decomposition.

Middle-метрики показывают, где проблема: retrieval recall, context overflow, duplicate chunks, citation mismatch или hallucination.

---

# 9. Верхнеуровневая архитектура продукта

```text
AutoAgent Optimizer
│
├── Problem & Constraint Definition
│
├── Golden Dataset Studio
│
├── Architecture Arena
│   ├── baseline generation
│   ├── equal-budget tournament
│   ├── promote / prune
│   └── deep optimization rounds
│
├── AgentOpt DSL + Graph IR
│
├── Renderer Layer
│   ├── LangGraph renderer
│   ├── Python node renderer
│   ├── MCP server wrapper / renderer
│   ├── API adapter renderer
│   └── test suite renderer
│
├── Component Factory
│   ├── capability gap detector
│   ├── component discoverer
│   ├── contract generator
│   ├── implementation selector
│   ├── optional implementation generator
│   ├── test generator
│   ├── sandbox runner
│   └── component registry
│
├── User Component Intake
│   ├── import MCP server
│   ├── import API endpoint
│   ├── import Python/TS package
│   ├── import Docker service
│   ├── validate against contract
│   └── register as candidate component
│
├── White-box Trace Runtime
│
├── Metrics & Oracle Engine
│   ├── output metrics
│   ├── middle metrics
│   ├── executable test oracles
│   ├── LLM judges
│   ├── human annotations
│   └── safety/security checks
│
├── Diagnostic Intelligence Layer
│   ├── bottleneck detection
│   ├── failure attribution
│   ├── materialize-as-code decisions
│   ├── architecture mutation suggestions
│   └── targeted intervention planning
│
├── Optimization Engine
│   ├── architecture search
│   ├── config search
│   ├── component implementation search
│   ├── prompt/program optimization
│   └── budget allocation
│
└── Evidence & Export Layer
    ├── champion config
    ├── challenger configs
    ├── LangGraph project export
    ├── generated/user-supplied component references
    ├── test suite
    ├── MCP/API bindings
    ├── CI gates
    └── evidence report
```

---

# 10. Architecture Arena

## 10.1. Назначение

Architecture Arena — слой, который генерирует, сравнивает и отбирает архитектурно разные baseline-решения.

Цель — не сразу тюнить один pipeline, а понять, какой тип решения лучше подходит для задачи.

## 10.2. Baseline families

Базовый каталог architecture templates:

1. Direct LLM;
2. Basic RAG;
3. RAG + reranker;
4. RAG + verifier;
5. Hierarchical RAG;
6. ReAct tool agent;
7. Plan-and-execute agent;
8. Router pipeline;
9. Deterministic + LLM hybrid;
10. Human-in-the-loop action workflow;
11. Multi-agent review/debate;
12. MCP-heavy tool workflow;
13. Code/test-driven agent;
14. Document processing pipeline;
15. OCR/table extraction pipeline.

## 10.3. Equal-budget tournament

Каждая architecture family получает одинаковый стартовый бюджет:

```text
N trials
M dataset cases
K dollars
T minutes
same judge/test suite fidelity
```

Цель первого раунда — выявить signal, а не найти глобальный optimum.

## 10.4. Promote / prune

После начального tournament система предлагает:

- удалить dominated architectures;
- сохранить promising architectures;
- дать дополнительный бюджет лидерам;
- вручную сохранить стратегически важную архитектуру;
- добавить новую architecture idea от человека.

## 10.5. Deep optimization

После отбора promising architectures запускается более глубокий поиск внутри каждой family.

---

# 11. AgentOpt DSL

## 11.1. Назначение DSL

DSL нужен для декларативного описания:

- задачи;
- ограничений;
- decision policy;
- architecture space;
- components;
- graph;
- optimizable parameters;
- metrics;
- datasets;
- HITL checkpoints;
- render targets;
- budgets;
- security policies.

DSL не должен быть привязан только к LangGraph. LangGraph — первый render target, но внутренний Graph IR должен быть runtime-neutral.

## 11.2. Основные сущности DSL

```text
mission
constraints
decision_policy
architecture_space
components
graph
nodes
edges
optimizable_params
implementation_space
component_contracts
datasets
metrics
oracles
optimization
hitl
security
render_targets
exports
```

## 11.3. Пример DSL

```yaml
mission:
  name: pdf_to_database_pipeline
  description: >
    Extract structured rows from complex PDF files and write them
    into a relational database staging table.

constraints:
  avg_cost_usd_per_document: <= 2.0
  p95_latency_seconds: <= 60
  db_schema_validity: >= 0.99
  pii_external_transfer: == 0
  human_review_rate: <= 0.2

decision_policy:
  mode: constrained_optimization
  optimize: row_extraction_accuracy
  secondary_objectives:
    minimize:
      - avg_cost_usd_per_document
      - p95_latency_seconds
      - human_review_rate
  hard_constraints:
    db_schema_validity: >= 0.99
    pii_external_transfer: == 0

architecture_space:
  generate:
    - vision_llm_extraction
    - text_layer_deterministic_extraction
    - ocr_first_pipeline
    - hybrid_deterministic_llm_repair
    - mcp_ocr_service_pipeline
    - hitl_low_confidence_review
  max_baselines: 8
  require_human_approval_before_execution: true

components:
  models:
    allowed:
      - openai:gpt-4.1-mini
      - local:qwen3-32b
      - local:vision-model
  services:
    allowed:
      - type: mcp_server
        name: user_ocr_server
        source: ./services/ocr-mcp-server
        contract: ./contracts/ocr_contract.yaml
  databases:
    - name: staging_db
      type: postgres

nodes:
  extract_pdf_tables:
    type: capability
    capability: structured_pdf_table_extraction
    implementation_space:
      allow_existing_tools: true
      allow_user_supplied_components: true
      allow_oss_libraries: true
      allow_mcp_servers: true
      allow_code_synthesis: true
      candidates:
        - type: user_supplied_mcp
          name: user_ocr_server
        - type: deterministic_python
          strategy: text_layer_first
        - type: deterministic_python
          strategy: ocr_first
        - type: hybrid
          strategy: deterministic_with_llm_repair
    contract:
      input_schema: PdfFile
      output_schema: ExtractedRows
      tests: ./tests/test_pdf_extraction.py
      min_test_pass_rate: 0.95
    metrics:
      output:
        - row_extraction_accuracy
        - field_normalization_accuracy
        - db_schema_validity
      middle:
        - ocr_confidence
        - table_detection_confidence
        - ambiguous_cell_rate
        - schema_validation_error_rate
      ops:
        - latency
        - memory_mb
        - cost

optimization:
  tournament:
    initial_budget_per_baseline_usd: 25
    initial_trials_per_baseline: 10
    promote_top_k: 3
  deep_search:
    budget_usd: 500
    max_trials: 300
    early_stopping: true
    allow_architecture_mutations: true

hitl:
  checkpoints:
    - architecture_review
    - component_contract_review
    - user_component_acceptance
    - generated_code_review
    - dataset_review
    - prune_promote_decision
    - champion_approval
```

---

# 12. Renderer Layer

## 12.1. Назначение

Renderer превращает AgentOpt DSL / Graph IR в исполняемые artifacts.

Первый target — LangGraph.

## 12.2. Render targets

MVP:

- LangGraph Python workflow;
- Python deterministic node;
- pytest suite;
- MCP client binding;
- API wrapper;
- Docker execution wrapper.

Future:

- LlamaIndex workflow;
- CrewAI workflow;
- AutoGen/Microsoft Agent Framework;
- TypeScript runtime;
- Temporal workflow;
- Kubernetes Job specs.

## 12.3. Что генерирует LangGraph renderer

- state schema;
- node functions;
- graph topology;
- conditional edges;
- retry/fallback logic;
- checkpointing;
- HITL interrupts;
- tracing hooks;
- metric hooks;
- config injection;
- tool/MCP bindings;
- component version references.

## 12.4. Что renderer не должен делать

Renderer не должен превращаться в arbitrary code generator. Он должен генерировать код только из typed Graph IR, templates и approved components.

---

# 13. Component Factory

## 13.1. Назначение

Component Factory — слой, который помогает закрывать missing capabilities в AI-пайплайне.

Он нужен потому, что зрелое решение часто требует не только LLM-конфигов, но и:

- deterministic validators;
- parsers;
- schema mappers;
- API wrappers;
- MCP servers;
- pytest suites;
- DB writers;
- OCR tools;
- business rule engines;
- sandboxed code runners;
- data transformation nodes.

## 13.2. Главный принцип

Component Factory не должна быть бесконтрольным codegen. Каждый компонент создаётся или подключается через contract-first workflow.

```text
Capability gap
  -> Component contract
  -> Reuse existing component if possible
  -> Accept user-supplied component if provided
  -> Generate wrapper or implementation if needed
  -> Generate / attach tests
  -> Run in sandbox
  -> Validate against contract
  -> Register as candidate implementation
  -> Evaluate inside pipeline
```

## 13.3. Build / Buy / Supply / Synthesize ladder

Для каждой missing capability система должна идти по лестнице:

### 1. Reuse

Найти готовый OSS/internal component.

### 2. Wrap

Если компонент существует, но не соответствует interface, создать wrapper.

### 3. User Supply

Если пользователь хочет реализовать компонент сам, система выдаёт контракт, тесты, ожидаемые schemas и integration harness. Пользователь пишет MCP server / API / библиотеку / Docker service в своей IDE и подключает обратно.

### 4. Compose

Собрать компонент из нескольких существующих pieces.

### 5. Synthesize

Сгенерировать bounded deterministic node или MCP skeleton.

### 6. Escalate

Если задача high-risk или не проходит tests, создать developer task для человека.

## 13.4. Capability Gap Detector

Ищет места, где LLM используется не по делу или где отсутствует нужная capability.

Примеры сигналов:

- LLM валидирует JSON вместо schema validator;
- LLM проверяет бизнес-правила, которые можно закодировать;
- LLM делает арифметику, даты, нормализацию валют;
- LLM повторно читает один и тот же документ;
- LLM извлекает поля, которые можно извлечь регулярным или layout-aware parser;
- pipeline не имеет pytest oracle для code-generation task;
- repeated tool failures показывают, что нужен deterministic pre-validator;
- OCR confidence низкая, но нет fallback;
- context window overflow показывает, что нужна compression/summarization node.

## 13.5. Component Contract

Каждый component должен иметь контракт:

```yaml
component:
  name: invoice_row_validator
  type: deterministic_node
  language: python

contract:
  purpose: Validate extracted invoice rows before DB insertion.

  inputs:
    rows:
      type: array
      items: InvoiceRow

  outputs:
    validation_result:
      type: object
      required:
        - is_valid
        - errors
        - warnings

  invariants:
    - amount must be decimal
    - currency must be ISO-4217
    - date must be ISO-8601
    - invoice_id must not be empty

  tests:
    framework: pytest
    path: ./tests/test_invoice_row_validator.py
    min_pass_rate: 1.0

  runtime:
    max_latency_ms: 200
    sandbox: docker

  permissions:
    network: false
    filesystem_read: false
    filesystem_write: false
    database_write: false

  observability:
    emit:
      - validation_error_count
      - warning_count
      - runtime_ms
```

## 13.6. User-supplied components

Пользователь может отказаться от generated implementation и реализовать компонент самостоятельно.

Поддерживаемые формы:

- MCP server;
- HTTP API;
- gRPC API;
- Python package;
- TypeScript package;
- Docker service;
- CLI tool;
- local executable;
- existing internal library;
- Git repository;
- prebuilt container image.

## 13.7. User Component Intake Flow

1. Система создаёт или утверждает component contract.
2. Пользователь экспортирует contract bundle:
   - input/output schemas;
   - test fixtures;
   - golden cases;
   - expected behavior;
   - failure modes;
   - security permissions;
   - integration harness.
3. Пользователь реализует компонент вне AutoAgent Optimizer.
4. Пользователь импортирует компонент обратно.
5. AutoAgent Optimizer запускает contract validation.
6. AutoAgent Optimizer запускает tests.
7. AutoAgent Optimizer прогоняет компонент в sandbox.
8. Компонент регистрируется как candidate implementation.
9. Optimizer сравнивает его с другими implementations.

## 13.8. Важно

User-supplied component не получает автоматического доверия. Он должен пройти:

- schema validation;
- contract tests;
- security policy checks;
- sandbox execution;
- observability compliance;
- optional human approval.

---

# 14. Golden Dataset Studio

## 14.1. Назначение

Golden Dataset Studio — встроенный модуль AutoAgent Optimizer, а не отдельный продукт. UX должен быть единым: пользователь задаёт задачу, собирает датасет, запускает architecture search и optimization в одном workflow.

## 14.2. Источники данных

- ручные examples;
- production traces;
- support tickets;
- documents;
- API logs;
- synthetic generation;
- adversarial generation;
- imported benchmarks;
- human annotations;
- failed production cases;
- regression cases.

## 14.3. Типы examples

- input-output examples;
- expected tool calls;
- expected retrieved documents;
- expected citations;
- expected refusal;
- expected escalation;
- expected DB rows;
- expected code patches;
- expected test results;
- expected human approval outcome.

## 14.4. Dataset lifecycle

1. Import.
2. Generate.
3. Deduplicate.
4. Cluster.
5. Review.
6. Annotate.
7. Split.
8. Version.
9. Lock holdout.
10. Use in optimization.
11. Refresh from production.

## 14.5. Dataset splits

- optimization/train set;
- validation set;
- holdout set;
- adversarial set;
- regression set;
- smoke set;
- shadow/canary set.

## 14.6. Leakage prevention

Система должна предотвращать:

- оптимизацию по holdout;
- изменение evaluator после сравнения без invalidating results;
- попадание synthetic near-duplicates в разные splits;
- prompt leakage из golden answers;
- overfitting к judge prompt.

---

# 15. Metrics & Oracle Engine

## 15.1. Категории метрик

### Output metrics

- task success;
- factual correctness;
- groundedness;
- answer completeness;
- conciseness;
- format validity;
- citation correctness;
- refusal correctness;
- user satisfaction proxy.

### Middle metrics

- retrieval recall;
- retrieval precision;
- context duplication rate;
- context window pressure;
- planner validity;
- tool selection correctness;
- tool argument validity;
- retry repetition rate;
- verifier disagreement rate;
- human escalation correctness;
- schema validation error rate.

### Operational metrics

- average cost;
- p50/p95/p99 latency;
- token usage;
- model call count;
- tool call count;
- memory usage;
- CPU/GPU usage;
- timeout rate;
- cache hit rate.

### Safety metrics

- PII leak rate;
- prompt injection success rate;
- jailbreak success rate;
- unauthorized tool call rate;
- unsafe output rate;
- policy violation rate;
- data exfiltration risk.

### Sovereignty metrics

- local model usage rate;
- EU-only execution rate;
- external provider dependency count;
- sensitive data external transfer rate;
- self-hosted component ratio.

## 15.2. Oracle types

Evaluator может быть любым executable oracle:

- pytest suite;
- schema validator;
- SQL constraint check;
- property-based test;
- integration test;
- snapshot test;
- LLM-as-judge;
- pairwise preference judge;
- human annotation;
- business metric proxy;
- red-team test;
- policy engine.

## 15.3. Приоритет executable tests

Если качество можно проверить deterministic способом, система должна предпочитать executable oracle, а не LLM judge.

Пример:

```text
Coding agent quality:
  pytest_pass_rate > LLM code quality score

PDF extraction quality:
  schema_validity + golden row match > LLM answer rating

API action quality:
  integration test result > LLM explanation
```

---

# 16. White-box Trace Runtime

## 16.1. Назначение

Trace Runtime собирает детальные traces по каждому execution run.

Система не должна оценивать pipeline как black box. Она должна видеть:

- какие nodes исполнялись;
- какие inputs/outputs были на каждом шаге;
- какие tools были вызваны;
- какие документы retrieved;
- какие retries произошли;
- какие validations failed;
- где выросла latency;
- где потрачены деньги;
- где возник context overflow;
- где был вызван human approval;
- какие deterministic tests упали.

## 16.2. Span types

- llm_call_span;
- retrieval_span;
- reranker_span;
- tool_execution_span;
- mcp_call_span;
- deterministic_node_span;
- validator_span;
- pytest_suite_span;
- db_write_span;
- human_review_span;
- sandbox_execution_span;
- policy_gate_span;
- cache_span.

## 16.3. Trace data для deterministic node

- input schema hash;
- output schema hash;
- implementation version;
- contract version;
- test version;
- runtime;
- memory;
- exceptions;
- validation errors;
- side effects;
- sandbox policy;
- permission usage;
- emitted metrics.

## 16.4. Replay

Система должна поддерживать replay для воспроизводимости:

- same dataset case;
- same config;
- same component versions;
- same prompt versions;
- same model versions where possible;
- same tool mocks where needed;
- deterministic component replay.

---

# 17. Diagnostic Intelligence Layer

## 17.1. Назначение

Diagnostic Intelligence Layer анализирует:

```text
architecture graph + traces + middle metrics + output metrics + neighboring experiments
```

И выдаёт:

```text
failure attribution + bottleneck detection + ranked interventions + next experiment plan
```

## 17.2. Примеры diagnostics

### Context overflow

```text
Finding:
  Context window pressure > 0.9 on 42% failed cases.

Likely cause:
  Flat RAG retrieves too many duplicate chunks.

Suggested interventions:
  - add chunk deduplication;
  - add reranker;
  - reduce top_k;
  - add hierarchical RAG;
  - add context compression.
```

### Invalid tool arguments

```text
Finding:
  31% tool calls fail schema validation.

Likely cause:
  Planner emits underspecified arguments.

Suggested interventions:
  - add tool argument validator;
  - add repair node;
  - split planner and executor;
  - use structured output model;
  - add few-shot examples for tool calls.
```

### LLM doing deterministic validation

```text
Finding:
  LLM validator checks rules that are fully deterministic.

Likely cause:
  Missing code validator.

Suggested intervention:
  Materialize as deterministic code node.

Expected impact:
  - lower cost;
  - lower latency;
  - higher stability;
  - easier auditability.
```

### Weak OCR extraction

```text
Finding:
  Table extraction accuracy low on scanned PDFs.

Likely cause:
  Text-layer strategy fails on image-only documents.

Suggested interventions:
  - add OCR-first branch;
  - add document type classifier;
  - add user-supplied OCR MCP server;
  - add human review for low-confidence rows.
```

## 17.3. Intervention families

### Prompt/model interventions

- mutate prompt;
- add few-shot examples;
- switch model;
- route hard cases to stronger model;
- use cheap model for low-risk nodes;
- add structured outputs.

### RAG interventions

- query rewriting;
- multi-query retrieval;
- reranker;
- hybrid search;
- metadata filters;
- hierarchical RAG;
- context compression;
- chunk deduplication;
- citation verification.

### Tool interventions

- schema validator;
- argument repair;
- tool permission gate;
- tool result summarizer;
- max tool-call budget;
- deterministic pre-check.

### Code interventions

- materialize as code;
- generate deterministic validator;
- generate parser;
- generate normalizer;
- generate schema mapper;
- generate pytest oracle;
- wrap user-supplied API;
- integrate user-supplied MCP server.

### Runtime interventions

- caching;
- fallback model;
- retry policy;
- circuit breaker;
- parallelization;
- early exit;
- confidence threshold.

### HITL interventions

- add human review;
- tune escalation threshold;
- add approval gate;
- route uncertain cases to human;
- create annotation queue.

## 17.4. Rule-based first, LLM-assisted second

MVP Diagnostic Engine should start with:

- rule-based diagnostics;
- comparative diagnostics against neighboring experiments;
- LLM-assisted explanation and proposal generation.

LLM should not be the only decision-maker. It should help interpret evidence, but interventions must be constrained by policies and contracts.

---

# 18. Optimization Engine

## 18.1. Три уровня оптимизации

### 1. Architecture Search

Сравнивает разные graph structures and architecture families.

### 2. Config Search

Оптимизирует параметры внутри конкретной architecture family:

- models;
- prompts;
- top_k;
- rerankers;
- thresholds;
- retry policies;
- context budget;
- temperature;
- tool limits;
- validator settings;
- HITL thresholds.

### 3. Component Implementation Search

Сравнивает разные implementations capability:

- generated deterministic node;
- user-supplied MCP server;
- OSS library wrapper;
- API endpoint;
- hybrid LLM fallback;
- pure LLM baseline.

## 18.2. Optimization modes

- maximize quality under cost cap;
- minimize cost above quality floor;
- minimize latency above quality floor;
- maximize safety under quality floor;
- Pareto exploration;
- sovereign-preferred mode;
- human-review-minimization mode;
- deterministic-first mode.

## 18.3. Budget allocation

Система должна поддерживать:

- initial equal budget per architecture;
- adaptive budget allocation;
- early stopping;
- multi-fidelity evaluation;
- repeated runs for noisy configs;
- holdout validation;
- red-team escalation only for promising candidates.

## 18.4. Multi-fidelity levels

Fidelity может означать:

- размер датасета;
- число повторов;
- качество judge model;
- глубину red-team;
- realistic tool integration vs mocks;
- production-like environment;
- human review coverage.

---

# 19. HITL Cockpit

## 19.1. Назначение

HITL Cockpit — интерфейс, где человек участвует в проектировании и контроле optimization workflow.

## 19.2. HITL checkpoints

1. Problem clarification.
2. Architecture review.
3. Dataset review.
4. Metric review.
5. Component contract review.
6. User-supplied component acceptance.
7. Generated code review.
8. MCP permissions approval.
9. Prune/promote decision.
10. Intervention approval.
11. Champion approval.
12. Deployment approval.

## 19.3. Human actions

Пользователь может:

- удалить baseline;
- добавить architecture idea;
- изменить objective policy;
- изменить cost/latency constraints;
- добавить dataset cases;
- разметить спорные examples;
- утвердить component contract;
- скачать contract bundle;
- реализовать MCP/API самостоятельно;
- импортировать user-supplied component;
- запретить generated code;
- сохранить weak architecture для strategic exploration;
- выбрать не самый качественный, а более дешёвый champion;
- потребовать дополнительный red-team pass.

---

# 20. User-supplied MCP/API/code components

## 20.1. Почему это важно

Для поддержания принципа открытости и инженерной зрелости нельзя заставлять пользователя “кодить внутри оптимизатора”. Если Component Factory предлагает слабое решение, пользователь должен иметь возможность:

1. взять contract;
2. уйти в свою IDE;
3. реализовать компонент как MCP server, API, library или service;
4. вернуться;
5. подключить компонент;
6. дать optimizer’у сравнить его с альтернативами.

Это сохраняет баланс:

- AutoAgent Optimizer не превращается в IDE;
- пользователь не ограничен generated code;
- компоненты остаются testable and comparable;
- продукт сохраняет open ecosystem philosophy.

## 20.2. Поддерживаемые форматы поставки

- local Python package;
- local TypeScript package;
- Git repository;
- Docker image;
- Docker Compose service;
- Kubernetes service;
- HTTP API;
- gRPC API;
- MCP server;
- CLI binary;
- shared library;
- existing internal tool.

## 20.3. Contract Bundle Export

Система должна уметь экспортировать bundle для разработчика:

```text
component-contract/
  contract.yaml
  input_schema.json
  output_schema.json
  fixtures/
  goldens/
  tests/
  README.md
  integration_harness.py
  docker-compose.example.yml
  mcp_server_template/
  api_openapi_template.yaml
```

## 20.4. Component Intake Validation

Импортированный компонент должен пройти:

- contract compatibility check;
- schema validation;
- fixture tests;
- golden tests;
- sandbox execution;
- permissions check;
- observability check;
- performance benchmark;
- security scan;
- optional human review.

## 20.5. Candidate comparison

После регистрации user-supplied component становится равноправным candidate:

```text
Capability: OCR extraction
Candidates:
  A. generated_python_ocr_node
  B. oss_wrapper_tesseract
  C. user_supplied_mcp_ocr_server
  D. vision_llm_fallback
```

Optimizer сравнивает их по:

- accuracy;
- latency;
- cost;
- memory;
- failure rate;
- confidence calibration;
- security;
- maintainability;
- deployment complexity.

---

# 21. OSS Ecosystem Reuse

## 21.1. Принцип

AutoAgent Optimizer должен строиться как OSS-first интеграционный слой.

## 21.2. Рекомендуемый OSS stack

| Layer | Primary OSS candidates | Role |
|---|---|---|
| Agent runtime / graph | LangGraph | First render target |
| Alternative runtimes | LlamaIndex, CrewAI, AutoGen | Future render targets |
| Tracing | OpenTelemetry, OpenInference | Unified traces |
| Observability backend | Phoenix, Langfuse, MLflow | Traces, evals, datasets, experiments |
| Prompt optimization | DSPy | Local prompt/program optimization |
| Dataset generation | Ragas, DeepEval | Synthetic goldens and evals |
| Red teaming | Promptfoo, Giskard | Safety/adversarial tests |
| Policy engine | OPA/Rego | Governance and deployment constraints |
| Optimization | Ax, BoTorch, Ray Tune, Optuna | Multi-objective search, early stopping |
| Model gateway | LiteLLM | Unified model access, budgets, routing |
| Local inference | vLLM, Ollama | Sovereign/local execution |
| Vector DB | pgvector, Qdrant, Weaviate, Milvus | RAG backends |
| Tests | pytest, mypy, ruff, semgrep | Executable code oracles |
| Sandboxing | Docker, gVisor, Firecracker-like isolation | Safe component execution |
| Storage | Postgres, MinIO/S3 | Metadata and artifacts |
| UI | React/Next.js | Control plane UI |
| Distributed execution | Ray, Kubernetes Jobs | Parallel experiments |
| Workflow backend | Temporal optional | Long-running orchestration |
| MCP | MCP SDKs and servers | Tool/service integration |

## 21.3. Собственный IP

Своё ядро продукта:

1. AgentOpt DSL;
2. Graph IR;
3. Architecture Template Catalog;
4. LangGraph renderer;
5. Architecture Arena;
6. Component Factory;
7. User Component Intake;
8. White-box metrics taxonomy;
9. Diagnostic Intelligence Layer;
10. intervention operators;
11. budget-aware tournament logic;
12. HITL Cockpit;
13. Evidence Pack format.

---

# 22. Security and Governance

## 22.1. Основные риски

- arbitrary code execution;
- malicious MCP server;
- secret leakage;
- prompt injection through tools;
- data exfiltration;
- unsafe side effects;
- unapproved DB writes;
- dependency supply-chain attacks;
- generated code vulnerabilities;
- PII in traces;
- evaluator leakage.

## 22.2. Security requirements

### SR-1. Sandbox by default

Generated and user-supplied components must run in sandbox unless explicitly trusted.

### SR-2. Least privilege

Every component must declare permissions:

- network;
- filesystem read/write;
- database read/write;
- external API access;
- secret access;
- tool access.

### SR-3. Policy gates

OPA/Rego-like policy layer should enforce:

- allowed providers;
- data residency;
- PII handling;
- side-effect permissions;
- deployment approval;
- production write restrictions.

### SR-4. Trace redaction

Traces must support redaction of:

- secrets;
- PII;
- credentials;
- customer data;
- confidential documents.

### SR-5. Component approval workflow

High-risk components require human approval before production use.

### SR-6. Reproducible artifacts

Champion export should include versions, hashes and dependencies.

---

# 23. Evidence Pack

## 23.1. Назначение

Evidence Pack — финальный отчёт, объясняющий, почему выбран champion.

## 23.2. Содержимое

- project summary;
- task definition;
- constraints;
- dataset version;
- architecture candidates;
- optimization budget;
- experiment summary;
- Pareto frontier;
- champion config;
- challenger configs;
- rejected architectures;
- metric table;
- confidence intervals where available;
- trace samples;
- failure taxonomy;
- diagnostics;
- interventions applied;
- component versions;
- generated code references;
- user-supplied component references;
- test results;
- red-team results;
- safety policy results;
- cost/latency breakdown;
- deployment recommendation;
- monitoring recommendations;
- known limitations.

## 23.3. Example champion explanation

```text
Champion: router_pipeline_v17

Why selected:
  - highest task success under cost cap;
  - 12.4 pp better than baseline;
  - 31% cheaper than RAG+Verifier alternative;
  - p95 latency within threshold;
  - zero unauthorized tool calls;
  - deterministic validator replaced LLM validator and reduced cost by 18%;
  - user-supplied OCR MCP server outperformed generated OCR node by 9 pp.

Known regressions:
  - slightly worse on long scanned PDFs with rotated tables;
  - higher human review rate on ambiguous invoices.

Recommended next step:
  - add 50 more golden cases for rotated scanned PDFs;
  - test table-structure repair node;
  - canary at 5% traffic.
```

---

# 24. Functional Requirements

## FR-1. Project creation

Система должна позволять создать optimization project из:

- natural language task description;
- YAML/JSON spec;
- imported existing agent;
- existing LangGraph project;
- API endpoint;
- dataset-only setup.

## FR-2. Architecture generation

Система должна генерировать несколько architecture candidates на основе task type, constraints, available tools and templates.

## FR-3. Architecture review

Пользователь должен иметь возможность редактировать, удалять, добавлять и утверждать architecture candidates перед запуском.

## FR-4. DSL

Система должна иметь декларативный DSL для описания mission, constraints, architecture space, graph, components, metrics, datasets, optimization и exports.

## FR-5. Graph IR

Система должна иметь runtime-neutral Graph IR, из которого можно рендерить LangGraph и будущие targets.

## FR-6. LangGraph renderer

Система должна рендерить approved graph specs в исполняемый LangGraph workflow.

## FR-7. Golden Dataset Studio

Система должна поддерживать import, generation, review, versioning и splitting golden datasets.

## FR-8. Executable oracles

Система должна поддерживать pytest, schema validators, integration tests and other executable oracles as first-class evaluators.

## FR-9. White-box tracing

Система должна собирать node-level and edge-level traces for LLM, retrieval, tools, MCP calls, code nodes, tests and human gates.

## FR-10. Middle metrics

Система должна считать middle metrics per node and per failure class.

## FR-11. Architecture tournament

Система должна запускать equal-budget tournament между architecture candidates.

## FR-12. Deep optimization

Система должна давать дополнительный бюджет promising architectures and optimize configs within them.

## FR-13. Diagnostic Intelligence

Система должна выявлять bottlenecks, failure modes and recommend targeted interventions.

## FR-14. Component Factory

Система должна уметь создавать, выбирать, оборачивать и тестировать bounded components based on contracts.

## FR-15. User-supplied components

Система должна позволять пользователю поставлять MCP/API/code components and validate them against contracts.

## FR-16. Component registry

Система должна хранить contracts, implementations, tests, versions, metrics and approvals for components.

## FR-17. Multi-objective optimization

Система должна поддерживать optimization policies with hard constraints and trade-offs.

## FR-18. Pareto frontier

Система должна показывать Pareto frontier and allow champion selection based on decision policy.

## FR-19. HITL checkpoints

Система должна поддерживать human approval and intervention at key checkpoints.

## FR-20. Export

Система должна экспортировать champion as deployable artifacts: code, config, prompts, tests, component references, CI gates and evidence report.

---

# 25. Non-functional Requirements

## NFR-1. OSS-first

Core should be self-hostable and extensible.

## NFR-2. Extensibility

Adapters, renderers, evaluators, optimizers, component types and templates must be plugin-based.

## NFR-3. Reproducibility

Experiments must be versioned and reproducible where possible.

## NFR-4. Security

Generated and user-supplied code must be sandboxed and policy-controlled.

## NFR-5. Observability

All executions must be traceable.

## NFR-6. Vendor neutrality

System should support multiple model providers, local models and multiple observability backends.

## NFR-7. Cost control

Every experiment must have budget tracking and stopping conditions.

## NFR-8. Data privacy

System must support trace redaction, local execution and provider restrictions.

## NFR-9. Human override

Human user must be able to override optimizer decisions.

## NFR-10. Progressive adoption

Users should be able to start with CLI/local mode and later move to UI/team/enterprise mode.

---

# 26. MVP Definition

## 26.1. MVP thesis

MVP should prove that AutoAgent Optimizer can compare architecture families, optimize within winners, use white-box traces, and incorporate deterministic components/tests.

## 26.2. Recommended MVP vertical

Best first demo/use case:

```text
Complex PDF/OCR extraction -> structured database rows
```

Why:

- pure LLM baseline is easy but weak;
- deterministic components clearly matter;
- tests are natural;
- MCP/API integration is plausible;
- middle metrics are meaningful;
- cost/latency/quality trade-offs are visible;
- user-supplied component flow can be demonstrated.

## 26.3. MVP components

### Must-have

1. DSL v0.
2. Graph IR v0.
3. LangGraph renderer.
4. 5–7 architecture templates.
5. Dataset Studio Lite.
6. JSONL dataset format.
7. Pytest oracle support.
8. White-box tracing v0.
9. Middle metrics v0.
10. Architecture Arena v0.
11. Random/grid/Optuna-style optimization.
12. Component Factory Lite.
13. User Component Intake Lite.
14. HITL review checkpoints.
15. Evidence report.
16. Champion export.

### Initial templates

- Direct LLM;
- Basic RAG;
- RAG + verifier;
- Deterministic + LLM hybrid;
- OCR-first document pipeline;
- MCP tool workflow;
- HITL low-confidence workflow.

### Initial Component Factory capabilities

- generate Python deterministic node skeleton;
- generate pytest skeleton;
- wrap HTTP API;
- wrap MCP server;
- validate user-supplied component against contract;
- run tests in sandbox;
- register component version.

### Initial middle metrics

- context window pressure;
- retrieval recall/precision;
- tool argument validity;
- schema validation pass rate;
- pytest pass rate;
- OCR confidence;
- ambiguous field rate;
- human review rate;
- cost;
- latency.

## 26.4. Not in MVP

- fully autonomous arbitrary code synthesis;
- full multi-runtime rendering;
- production canary;
- enterprise RBAC;
- marketplace;
- advanced causal diagnosis;
- full IDE integration;
- complex distributed execution at large scale.

---

# 27. Roadmap

## Phase 0. Research prototype

- DSL draft;
- few architecture templates;
- manual experiment runner;
- simple metrics;
- one LangGraph renderer;
- one demo dataset.

## Phase 1. OSS MVP

- CLI;
- local runner;
- LangGraph renderer;
- Architecture Arena;
- Dataset Studio Lite;
- Component Factory Lite;
- user-supplied MCP/API import;
- evidence report;
- docs and examples.

## Phase 2. Team UI

- web UI;
- HITL Cockpit;
- experiment dashboard;
- trace viewer;
- Pareto explorer;
- component registry UI;
- dataset review UI.

## Phase 3. Enterprise readiness

- RBAC;
- SSO;
- audit logs;
- policy packs;
- Kubernetes execution;
- sandbox hardening;
- enterprise connectors;
- private model gateway;
- sovereign deployment.

## Phase 4. Ecosystem

- plugin marketplace or registry;
- community templates;
- community evaluators;
- community component contracts;
- reusable architecture packs;
- benchmark suites.

---

# 28. Open Questions

1. Какой язык DSL выбрать: YAML-first или Python SDK-first?
2. Должен ли Graph IR быть отдельным публичным стандартом?
3. Какой backend observability выбрать первым: Phoenix, Langfuse или MLflow?
4. Насколько глубоко в MVP поддерживать MCP?
5. Где проходит граница между Component Factory и IDE/developer workflow?
6. Как безопасно запускать user-supplied code локально и в cloud?
7. Какой формат Evidence Pack сделать стандартным?
8. Нужно ли делать hosted version сразу или сначала только OSS/local?
9. Как лицензировать OSS core: Apache 2.0 или другой вариант?
10. Как предотвратить overfitting optimizer к golden dataset?
11. Как калибровать LLM-as-judge и совмещать его с deterministic oracles?
12. Как измерять maintainability generated/user-supplied components?

---

# 29. Core Differentiation

AutoAgent Optimizer отличается от существующих инструментов тем, что объединяет пять вещей:

## 1. Architecture search

Он сравнивает не только prompts, а архитектурно разные AI-решения.

## 2. White-box evaluation

Он оценивает внутренние шаги pipeline, а не только финальный output.

## 3. Component-level optimization

Он оптимизирует не только LLM calls, но и deterministic code, validators, tests, APIs and MCP services.

## 4. HITL co-architecture

Человек участвует в проектировании, pruning, approval, contract review and final decision.

## 5. OSS-first composability

Он переиспользует существующую OSS-экосистему и позволяет пользователю приносить собственные компоненты.

---

# 30. Final Concept Statement

**AutoAgent Optimizer** — это OSS-first платформа для поиска, генерации, диагностики и оптимизации compound AI systems. Она автоматически создаёт и сравнивает архитектурно разные baseline-решения, описывает их через декларативный DSL, рендерит в исполняемые workflow, подключает LLM, deterministic code, tests, MCP/API components, retrieval, tools и HITL-гейты, оценивает систему через white-box traces и middle-метрики, находит bottlenecks, предлагает targeted interventions, позволяет пользователю поставлять собственные компоненты по контракту, проводит budget-aware optimization и возвращает deployable champion с доказательной базой.

Главная философия продукта:

> Не всё должно быть LLM. Не всё должно быть кодом. Хорошая AI-система — это найденный и доказанный баланс между LLM, deterministic software, tools, tests, human judgement and runtime constraints.

Главная инженерная формула:

```text
Design many architectures.
Measure them as white boxes.
Move deterministic work out of LLM where possible.
Let humans intervene where judgement matters.
Optimize under real constraints.
Export evidence, not vibes.
```

