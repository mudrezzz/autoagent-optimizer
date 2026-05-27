# Frontend Architecture v0

## Purpose

Зафиксировать целевую архитектуру фронтенда AutoAgent Optimizer в формате `React + TypeScript`, чтобы:

1. не переделывать UI на каждом слайсе;
2. развивать функционал итерационно через "разблокировку" capability;
3. держать синхронность `Backend + Frontend + Demo + QA`.

Документ задает каркас рабочего приложения (а не временной заглушки), где недоступные функции видимы, но помечены как `planned/locked` до готовности backend-контрактов.

## Scope v0

Входит в v0:

1. архитектурный каркас SPA на `React + TypeScript`;
2. стабильные UI-контракты capability C1..C6;
3. стратегия состояния, роутинга и исполнения run;
4. интеграция с дизайн-системой как обязательный стандарт;
5. правила тестирования фронтенда и demo-acceptance.
6. модель wizard-навигации с разблокировкой шагов по готовности.

Не входит в v0:

1. полный production-уровень auth/tenant model;
2. финальный real-time transport (SSE/WebSocket) для всех сценариев;
3. exhaustive UI-покрытие всех будущих advanced-функций.

## Design Principles

1. `Product-shaped shell first`: сразу строим структуру конечного приложения.
2. `Capability unlock model`: UI экраны есть заранее, но активируются по мере готовности backend.
3. `Stable contracts first`: типы запросов/ответов фиксируются до расширения функционала.
4. `Observable by default`: каждый run и шаг отображаются в trace/diagnostics.
5. `Design-system only`: UI строится строго по `design_system`.
6. `UX North Star first`: визуальная и поведенческая композиция строится по референсу `design_system/screenshots/app-v3.png`.

## UX North Star (app-v3)

Базовый UX-референс для workbench-интерфейса:

1. [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png)

Обязательные принципы композиции:

1. Для `Battle Workspace` сохраняется app-v3 композиция как North Star.
2. Для `Battles Hub` используется упрощенная композиция без правого rail.
3. run-centric header, KPI и intervention rail относятся только к `Battle Workspace`.
4. Важные действия проекта (`compare`, `promote champion`, `apply intervention`, `export`) живут в `Battle Workspace`.
5. Новые capability встраиваются в композицию `Battle Workspace`, а не в `Battles Hub`.

Это не "пиксель-перфект копия", а обязательная продуктовая рамка UX-структуры.

## Tech Stack

1. `React 19+` (functional components, hooks).
2. `TypeScript` (strict mode).
3. `Vite` как dev/build toolchain.
4. `React Router` для app routing.
5. `TanStack Query` для server state и polling.
6. `Zustand` (или эквивалентный lightweight store) для локального app state.
7. `Vitest + Testing Library + Playwright` для unit/integration/e2e.

## High-Level Topology

```text
Browser (React/TS SPA)
  -> Frontend API Client (typed)
  -> Backend API (optimizer services / BFF)
  -> Execution Runtime (DSL run / Native run / Evaluation runners)
  -> Artifacts (reports, traces, evidence packs)
```

## Application Information Architecture

Ключевая SaaS-оговорка:

1. В пользовательском UX основной объект — `Battle` (арена оптимизации).
2. Пользователь сначала попадает на отдельный список своих проектов.
3. Внутри конкретного проекта открывается отдельный рабочий экран проекта.

Основные экраны:

1. `Battles Hub` (только список battle-проектов клиента + создание battle).
2. `Battle Workspace` (чат, кандидаты, датасеты, метрики, раны, отчеты, champion).
3. `Settings`.

Разделы внутри `Battle Workspace`:

1. `Battle Chat`
2. `Candidates`
3. `Datasets`
4. `Metrics`
5. `Evaluators`
6. `Optimizer Runs`
7. `Reports`
8. `Champion`

Каждый раздел имеет:

1. `enabled` (функция доступна);
2. `planned` (функция видна, но еще закрыта);
3. `beta` (функция доступна с пометкой ограничений).

Важное правило IA:

1. Левое меню `Battle Workspace` работает как последовательный wizard, а не только как статическая навигация.
2. Следующие шаги становятся доступными только после выполнения prerequisite-условий предыдущих шагов.

## Core User Flow (v0 target)

Центральный flow для пользователя:

1. Пользователь открывает `Battles Hub` и видит только свои battle-проекты.
2. Создает новый проект (workspace) или открывает существующий.
3. Переходит в отдельный `Battle Workspace`.
4. В правой панели `Battle Chat` формулирует задачу естественным языком.
5. В центральной панели видит список кандидатов как читабельные строки с ключевыми метриками.
5.  предлагает кандидатов на базе pattern library + ограничений пользователя.
6. Пользователь подтверждает/исключает паттерны, получает набор candidate-агентов.
7. Система внутренне валидирует/компилирует кандидатов (без ручной DSL-работы).
8. Пользователь формирует dataset (ручной ввод/загрузка/-синтез/очистка).
9. Пользователь задает comparative/diagnostic метрики (отдельный шаг).
10. Пользователь настраивает evaluators и матрицу `Evaluator x Metric` (отдельный шаг).
11. Пользователь задает optimizer policy и budget.
12. Запускает оптимизацию, наблюдает прогресс/логи/метрики в глубину.
13. Получает аналитический отчет, выбирает winner.
14. Экспортирует champion в native.
15. Опционально импортирует измененный native agent обратно и повторяет цикл оценки.

## Layout Rules (SaaS)

Обязательные правила компоновки:

1. На `Battles Hub` нет правого operational rail.
2. Левый каркас (navigation/settings zone) не уезжает при прокрутке.
3. Нижний блок профиля/настроек всегда прибит к низу viewport.
4. Прокрутка должна происходить в контентной области, а не во всем app-shell.
5. Capability-меню C2..C6 не показывается на `Battles Hub`; оно живет в `Battle Workspace`.

## Multi-User and Tenant Scope

Frontend изначально проектируется как multi-tenant SaaS:

1. Любой список проектов отображает только tenant-scoped данные пользователя.
2. Активный контекст в UI: `tenant -> project`.
3. Доступ к проекту по id всегда подтверждается backend (нельзя доверять только frontend state).

## Capability Contract Model

`/api/capabilities` возвращает каталог функций, которым управляется доступность UI:

1. `id`;
2. `title`;
3. `status` (`enabled|planned|beta|disabled`);
4. `routes`;
5. `required_backends`;
6. `notes`.

Product capability map (новая целевая модель):

1. `C1` Battle Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset Studio
5. `C5` Metrics Studio
6. `C6` Evaluators Studio
7. `C7` Optimizer Run Monitor
8. `C8` Report + Champion Export/Import

Frontend не "угадывает" готовность, а читает capability-манифест от backend.
Переходный режим допускает совместимость с legacy-ярлыками capability на период миграции.

## Frontend Module Boundaries

1. `app/`
2. `pages/`
3. `widgets/`
4. `features/`
5. `entities/`
6. `shared/`
7. `processes/`

Рекомендуемая ответственность:

1. `app`: bootstrapping, providers, router.
2. `pages`: route-level composition.
3. `widgets`: крупные UI-блоки экранов.
4. `features`: user actions/use-cases (run arena, export champion).
5. `entities`: доменные модели (profile, run, candidate, metric).
6. `shared`: UI-kit wrappers, utils, api client.
7. `processes`: длинные бизнес-потоки (benchmark loop, post-export loop).

## State Model

Разделение состояния:

1. `Server state`: TanStack Query (`workspaces`, `projects`, `candidates`, `datasets`, `runs`, `reports`, `capabilities`).
2. `Session/UI state`: выбранный battle/arena, активные панели, фильтры, layout.
3. `Project state machine`: `draft -> candidate_design -> candidate_ready -> dataset_ready -> run_ready -> running -> analyzed -> champion_selected`.

Ключевые сущности UI:

1. `WorkspaceEnvelope`
2. `ProjectEnvelope`
3. `CandidateSetEnvelope`
4. `RunEnvelope`

`RunEnvelope` минимум содержит:

1. `run_id`;
2. `project_id`;
3. `versions_manifest` (agents/datasets/metrics/evaluators/prompts/tools/settings);
4. `status`;
5. `comparative_metrics`;
6. `diagnostic_signals`;
7. `artifacts`.

## Wizard Gating Model

Левое меню `Battle Workspace` подчиняется state-machine шагов:

1. `locked`
2. `available`
3. `in_progress`
4. `completed`
5. `blocked`

Базовые зависимости v0:

1. `C3` доступен после выбора/открытия battle и входа в task-chat контур.
2. `C4` доступен после того, как сформирован candidate set (минимум 1 кандидат).
3. `C5` (Metrics) доступен после выбора кандидатов на тесты.
4. `C6` (Evaluators) доступен после определения хотя бы одного comparative metric.
5. `C7` (Optimizer) доступен после валидного `dataset + metrics + evaluators + budget` preflight.
6. `C8` (Report/Champion) доступен после завершенного optimizer run.

## API Contract Strategy

Правило: UI работает только с типизированными DTO и runtime-validation на границе (zod/io-ts эквивалент).

Минимальные контракты:

1. health/capabilities;
2. tenant-scoped projects CRUD/list;
3. chat task brief + candidate generation session;
4. pattern library retrieval & selection/exclusion;
5. internal candidate validate/compile readiness;
6. dataset/metrics/evaluator configuration;
7. optimizer run orchestration & monitoring;
8. evidence/champion artifacts metadata;
9. native import/export + compatibility/preflight results.

Любое изменение backend-формата:

1. сначала фиксируется в spec/ADR;
2. затем обновляются TS-типы и контрактные тесты;
3. только после этого расширяется UI.

## C2 Compile Readiness Gate (V2.3.S4)

Реализованный контракт C2 compile gate:

1. `POST /api/arenas/{arena_id}/candidates/select-for-tests` принимает пользовательский выбор кандидатов и запускает внутреннюю подготовку к тестам.
2. `candidate_set_draft.compile_gate` возвращает агрегированный статус (`draft|ready|failed`) и счетчики `ready/failed/total`.
3. `candidate.compile_readiness` возвращает детальный статус кандидата:
4. `status`, `dsl_file`, `compile_summary`, `issues`, `graph_ir_summary`, `compiled_at`.
5. Внутренний процесс подготовки делает несколько auto-retry попыток и пробует auto-fix `dsl_stub_ref`; issue показывается пользователю только если подготовка не удалась после этих попыток.

UX-ожидание:

1. пользователь отмечает кандидатов чекбоксами в списке;
2. пользователь запускает короткое действие `Select for tests`;
3. в UI не требуется отдельный ручной шаг "validate/compile", это внутренний процесс;
4. в аккордеоне кандидата issue-панель показывается только в fail-сценарии после внутренних попыток исправления.

## Comparative Metrics vs Diagnostic Signals in UI

UI отображает два разных слоя:

1. `Comparative Metrics`:
2. `Diagnostic Signals`:

`Comparative Metrics`:
1. используются для ranking и выбора winner;
2. нормализуются для сравнения разных кандидатов;
3. показываются как scoreboard/leaderboard.

`Diagnostic Signals`:
1. не участвуют напрямую в финальном ранжировании (если не задано иное профилем);
2. показывают "где именно ломается пайплайн" по шагам;
3. используются для точечного улучшения архитектуры.

Для разнотипных задач состав обоих слоев задается профилем оценки, а не хардкодом в UI.

Правило доступности метрик:

1. Метрики появляются/скрываются в зависимости от feature-map выбранных candidate-агентов.
2. Если у candidate-set нет retrieval-stage, retrieval comparative метрики недоступны.
3. Такие метрики могут оставаться diagnostic для отдельных кандидатов с соответствующим stage.

## Evaluator x Metric Matrix

`Evaluators` задаются отдельно от `Metrics` и связываются через матрицу:

1. одна метрика может оцениваться разными evaluator-стратегиями;
2. один evaluator может обслуживать несколько метрик;
3. допускается гибридная схема:
4. retrieval-метрика через dataset-oracle, итоговое качество через LLM-as-judge.

Optimizer preflight проверяет покрытие: каждая comparative метрика должна иметь хотя бы один evaluator.

## Dataset Contract Direction (Stage-aware)

Dataset v2 не ограничивается только `input + final output`:

1. `target_stage`: `retrieval | rerank | synthesis | final`;
2. expected может быть stage-specific (`evidence ids`, `ranked list`, `structured output`, `final answer`);
3. поддерживаются входные ресурсы типа `document set / archive` для retrieval-oriented тестов.

Это позволяет корректно валидировать метрики вроде `retrieval coverage`, а не только final response quality.

## Contextual Chat Behavior

Правый чат является автоматизацией активной capability:

1. на вкладке `Datasets` чат помогает с генерацией/чисткой/редактированием dataset;
2. на вкладке `Metrics` чат предлагает и объясняет метрики;
3. на вкладке `Evaluators` чат помогает собирать evaluator x metric matrix;
4. при смене capability меняется контекст ассистента и допустимые действия.

## Runtime Snapshot UX Policy

`Runtime snapshot` не должен перекрывать основной контент capability-экрана:

1. основной режим: скрыт из рабочего полотна;
2. debug-режим: доступен в отдельном drawer/panel;
3. в пользовательском режиме не влияет на скролл и визуальную иерархию.

## Budget and Cost UX

UI должен явно показывать:

1. бюджет профиля (`max_cases`, `max_llm_calls`, `max_cost_usd`, `timebox`);
2. фактическое потребление;
3. причину остановки (`budget_exceeded`, `manual_stop`, `completed`).

Единицы измерения:

1. `llm_calls_total` (шт.);
2. `cost_usd_total` (USD);
3. `latency_ms_p50/p95` (мс).

## Design System Compliance

Обязательные правила:

1. токены только из `design_system/colors_and_type.css`;
2. композиции и паттерны из `design_system/ui_kits/app/*`;
3. бренд-ассеты только из `design_system/assets/*`;
4. voice/copy по правилам `design_system/README.md`.

Нарушение этих правил блокирует приемку frontend-слайса.

## Testing Strategy (Frontend)

Тестовая пирамида:

1. unit: hooks, formatters, state reducers, DTO-mappers;
2. integration: page + API mock contracts;
3. e2e: ключевые user flows в браузере на локальном стенде.

Минимум для каждого frontend-слайса:

1. unit-тесты нового доменного кода;
2. integration-тест экранного поведения;
3. e2e smoke для основного happy-path.

Test gates для frontend delivery:

1. `Fast gate` (frontend-only): `python -m pytest tests/unit/test_frontend_contracts.py` + `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`.
2. `Targeted gate` (frontend + API-срез): fast gate + `python -m pytest tests/integration/test_frontend_dev_server.py` + профильные backend integration/e2e тесты по затронутым endpoint.
3. `Full gate` (крупный слайс/release): `python -m pytest` + frontend test suite.

Операционное правило: после изменения backend API frontend обязан работать против перезапущенного dev server; иначе возможны ложные `404` на `/api/*` из-за старого процесса.

## Demo Contract (v0)

Демо должно показывать не "мок-страницу", а рабочий контур:

1. загрузка capability-каталога;
2. запуск минимум одного реального backend-сценария;
3. отображение ranking + diagnostics;
4. переход к champion/export артефактам.

## Delivery Plan Alignment

Frontend развивается вертикально, синхронно с backend:

1. в каждом слайсе фиксируется, какие capability стали `enabled`;
2. UI для остальных capability остается видимым (`planned`);
3. Roadmap обновляется по модели `BE + FE + Demo + QA` в одном слайсе.
4. Для каждого закрытого frontend-слайса обновляется wiki (`docs/wiki/user_guides/*`, `docs/wiki/developer/*`, `docs/wiki/releases/*`).

## Missing Elements (Gap Analysis)

Ключевые пробелы относительно целевого продукта:

1. `FE` отсутствует основной `Battle Chat` как точка постановки задачи.
2. `FE` отсутствует библиотека паттернов с include/exclude UX.
3. `FE` отсутствуют `Dataset Studio` и `Metrics Studio`.
4. `FE` отсутствует продуктовый run-monitor с версиями сущностей и эпохами.
5. `FE` отсутствует путь native `import` (есть export/read-only артефакты).
6. `BE` отсутствует chat-orchestrator для candidate generation.
7. `BE` отсутствует pattern library service + RAG index/query API.
8. `BE` отсутствует unified version-manifest service для runs.
9. `BE` отсутствует native import pipeline с compatibility/preflight по коду.

Приоритет закрытия gap:

1. сначала `Workspaces + Battle Chat + Candidate lifecycle`;
2. затем `Dataset/Metrics/Optimizer setup`;
3. затем `Run monitor/report/champion`;
4. затем `native import` как замыкание пост-экспортного цикла.

## Definition of Done for Frontend Slice

Слайс считается завершенным, если:

1. backend-контракт реализован и задокументирован;
2. capability отражена в UI c корректным статусом;
3. дизайн-система соблюдена;
4. тесты `unit + integration + e2e` добавлены;
5. demo-сценарий обновлен и воспроизводим по README.

## Risks and Mitigations

1. Риск: рассинхрон frontend/backend контрактов.
2. Митигируем: typed client + contract tests + ADR/spec-first.
3. Риск: рост сложности UI при добавлении функций.
4. Митигируем: capability gating + модульные границы + state machine.
5. Риск: деградация UX при быстрых итерациях.
6. Митигируем: design-system gate и demo-acceptance на каждом слайсе.

## References

1. [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
2. [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
3. [Project_Operating_Model.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)
4. [ADR-0029](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0029-vertical-product-slices-backend-frontend-demo-sync.md)
5. [ADR-0030](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0030-design-system-as-mandatory-frontend-standard.md)

