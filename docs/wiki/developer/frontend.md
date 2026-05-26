# Frontend Guide

## C2 UI contract

В списке кандидатов:

1. Чекбокс выбора кандидата в тестовый набор.
2. Кнопка `Select for tests` для запуска внутренней подготовки.
3. Детали кандидата через accordion.

## C3 UI contract

В библиотеке паттернов:

1. Одна галочка `selected` на строку паттерна.
2. Кнопка `Save` сохраняет текущий набор выбранных паттернов.
3. До `Save` изменения остаются локальными (`dirty` state).
4. Детали паттерна доступны через accordion (не меняют selection).

## UX принципы

1. Валидация/компиляция скрыты как внутренний технический шаг.
2. Пользователь взаимодействует только с business-action: выбор кандидатов для тестов.
3. Selection-паттерн унифицирован между C2/C3: single-checkbox + explicit save action.
4. Ошибки показываются только если автоисправление не помогло.

## Тесты

1. `frontend/src/__tests__/app.workspace.test.tsx`

## C4 UI contract

В C4 Dataset Studio:

1. Экран разделен на два режима: `list` и `edit`.
2. В `list` режиме dataset-ы отображаются как candidate-like rows с чекбоксами.
3. Кнопка `Save` сохраняет назначение выбранных dataset-ов на арену.
4. `Details` раскрывает превью первых 5 строк.
5. `Edit` открывает отдельный editor-screen с breadcrumbs.
6. В `edit` режиме доступны add/delete/edit rows, JSONL import, `Save changes`, `Validate`, `Save version`.

В C4 Metrics & Evaluators Studio:

1. Comparative metrics редактируются чекбоксами + weight и сохраняются `Save metrics`.
2. Diagnostic signals редактируются чекбоксами и сохраняются `Save diagnostics`.
3. Evaluators редактируются чекбоксами и сохраняются `Save evaluators`.
4. Budget редактируется числами и сохраняется `Save budget`.
5. `Validate profile` возвращает status + issues.
6. `Save version` фиксирует snapshot evaluation profile.

Состояние загружается через `fetchArenaDatasetState` + `fetchArenaEvaluationState` и обновляется после каждого C4 действия.

## C5 UI contract

В C5 Optimizer Setup:

1. `Methods` и `Optimization controls` редактируются чекбоксами.
2. `Run plan` и `Budget limits` редактируются числовыми полями.
3. `Save setup` сохраняет профиль в backend.
4. `Validate` запускает preflight guardrails и возвращает status + issues.
5. `Launch` создает queued run только если guardrails не содержат error.
6. `Save profile version` фиксирует snapshot optimizer setup.
7. `Launch queue` показывает последние run-записи.

Состояние C5 загружается через `fetchArenaOptimizerState` и обновляется после каждого C5 действия.
