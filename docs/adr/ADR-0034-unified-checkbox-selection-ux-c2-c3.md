# ADR-0034: Unified Single-Checkbox Selection UX for C2 and C3

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S4a
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c3-pattern-selection.md

## Context

В Battle Workspace появилось расхождение в ключевом пользовательском действии выбора:

1. В C2 кандидаты выбираются одной галочкой на строку + явным действием сохранения/подготовки.
2. В C3 был отдельный паттерн `Include`/`Exclude`, который не совпадал с C2 и усложнял UX.

Разный паттерн взаимодействия для одного и того же класса действия (selection) увеличивает когнитивную нагрузку, ухудшает предсказуемость UX и замедляет поток пользователя.

## Decision

1. Для selection-действий в C2/C3 используем единый UI-паттерн: одна галочка на строку.
2. В C3 убираем UI-модель `Include/Exclude` и переходим на `selected/unselected`.
3. В C3 вводим явное батч-действие `Save`, аналогичное C2-подходу:
   - отметил галочки -> нажал `Save` -> паттерны учитываются;
   - снял галочки -> нажал `Save` -> паттерны не учитываются.

## Alternatives Considered

1. Оставить кнопки в C3 и чекбоксы в C2.
2. Перевести C2 на кнопки для симметрии.
3. Оставить tri-state модель `include/exclude/neutral` в пользовательском интерфейсе.

## Consequences

### Positive

1. Единая моторика выбора по всему Battle Workspace.
2. Более предсказуемое поведение для пользователя.
3. Проще тестировать и поддерживать frontend-контракты selection flow.

### Negative / Trade-offs

1. Нужна явная обработка состояния `dirty` перед сохранением.
2. Нужны UX-тесты на сценарий `toggle -> Save`.

## Implementation Notes

1. Изменение ограничено UI-слоем C3; backend API-контракт `saveArenaPatternSelection` не меняется.
2. В backend продолжаем передавать `include_pattern_ids`, а `exclude_pattern_ids` отправляем пустым массивом.
3. Добавлены frontend-тесты на сценарий явного сохранения C3 selection через кнопку `Save`.
4. Документация обновляется через wiki release-note и user guide.

## Verification

1. `npm run test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/unit/test_frontend_contracts.py -q`
3. `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py -q`

## Links

1. `Roadmap.md` (`V2.3.S4a`)
2. `frontend/src/App.tsx`
3. `frontend/src/__tests__/app.workspace.test.tsx`
4. `docs/wiki/releases/v2.3.s4a.md`
5. `docs/wiki/user_guides/c3-pattern-selection.md`
