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

1. Для `Project Workspace` сохраняется app-v3 композиция как North Star.
2. Для `Projects Hub` используется упрощенная композиция без правого rail.
3. run-centric header, KPI и intervention rail относятся только к `Project Workspace`.
4. Важные действия проекта (`compare`, `promote champion`, `apply intervention`, `export`) живут в `Project Workspace`.
5. Новые capability встраиваются в композицию `Project Workspace`, а не в `Projects Hub`.

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

1. В пользовательском UX `Workspace = Project`.
2. Пользователь сначала попадает на отдельный список своих проектов.
3. Внутри конкретного проекта открывается отдельный рабочий экран проекта.

Основные экраны:

1. `Projects Hub` (только список проектов клиента + создание проекта).
2. `Project Workspace` (чат, кандидаты, датасеты, метрики, раны, отчеты, champion).
3. `Settings`.

Разделы внутри `Project Workspace`:

1. `Project Chat`
2. `Candidates`
3. `Datasets`
4. `Metrics & Evaluators`
5. `Optimizer Runs`
6. `Reports`
7. `Champion`

Каждый раздел имеет:

1. `enabled` (функция доступна);
2. `planned` (функция видна, но еще закрыта);
3. `beta` (функция доступна с пометкой ограничений).

## Core User Flow (v0 target)

Центральный flow для пользователя:

1. Пользователь открывает `Projects Hub` и видит только свои проекты.
2. Создает новый проект (workspace) или открывает существующий.
3. Переходит в отдельный `Project Workspace`.
4. В `Project Chat` формулирует задачу естественным языком.
5. ИИ предлагает кандидатов на базе pattern library + ограничений пользователя.
6. Пользователь подтверждает/исключает паттерны, получает набор candidate-агентов.
7. Система внутренне валидирует/компилирует кандидатов (без ручной DSL-работы).
8. Пользователь формирует dataset (ручной ввод/загрузка/ИИ-синтез/очистка).
9. Пользователь настраивает метрики/evaluators и optimizer policy.
10. Запускает оптимизацию, наблюдает прогресс/логи/метрики в глубину.
11. Получает аналитический отчет, выбирает winner.
12. Экспортирует champion в native.
13. Опционально импортирует измененный native agent обратно и повторяет цикл оценки.

## Layout Rules (SaaS)

Обязательные правила компоновки:

1. На `Projects Hub` нет правого operational rail.
2. Левый каркас (navigation/settings zone) не уезжает при прокрутке.
3. Нижний блок профиля/настроек всегда прибит к низу viewport.
4. Прокрутка должна происходить в контентной области, а не во всем app-shell.
5. Capability-меню C2..C6 не показывается на `Projects Hub`; оно живет в `Project Workspace`.

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

1. `C1` Workspace & Project Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset & Metrics Studio
5. `C5` Optimizer Run Monitor
6. `C6` Report + Champion Export/Import

Frontend не "угадывает" готовность, а читает capability-манифест от backend.

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
2. `Session/UI state`: выбранный workspace/project, активные панели, фильтры, layout.
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

После каждого слайса обязателен полный прогон `python -m pytest` плюс фронтовые тесты (`vitest`, `playwright` после ввода toolchain).

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

## Missing Elements (Gap Analysis)

Ключевые пробелы относительно целевого продукта:

1. `FE` отсутствует корректное разделение `Projects Hub` и `Project Workspace`.
2. `FE` отсутствует основной `Project Chat` как точка постановки задачи.
3. `FE` отсутствует библиотека паттернов с include/exclude UX.
4. `FE` отсутствуют `Dataset Studio` и `Metrics Studio`.
5. `FE` отсутствует продуктовый run-monitor с версиями сущностей и эпохами.
6. `FE` отсутствует путь native `import` (есть export/read-only артефакты).
7. `FE` не зафиксированы sticky правила app-shell для SaaS-навигации.
8. `BE` отсутствует tenant/user-bound access enforcement для project API.
9. `BE` отсутствует chat-orchestrator для candidate generation.
10. `BE` отсутствует pattern library service + RAG index/query API.
11. `BE` отсутствует unified version-manifest service для runs.
12. `BE` отсутствует native import pipeline с compatibility/preflight по коду.

Приоритет закрытия gap:

1. сначала `Workspaces + Project Chat + Candidate lifecycle`;
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
