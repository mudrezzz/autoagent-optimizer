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

Состояние загружается через `fetchArenaDatasetState` и обновляется после каждого C4 действия.
