# ADR-0034: Unified Checkbox Selection UX for C2 and C3

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S4a
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c3-pattern-selection.md

## Context

В Battle Workspace появилось расхождение в ключевом пользовательском действии выбора:

1. В C2 кандидаты выбираются чекбоксами.
2. В C3 паттерны выбираются кнопками `Include` / `Exclude`.

Разный паттерн взаимодействия для одного и того же класса действия (selection) увеличивает когнитивную нагрузку, ухудшает предсказуемость UX и замедляет поток пользователя.

## Decision

1. Для selection-действий в C2/C3 используем единый UI-паттерн: чекбоксы.
2. В C3 оставляем доменную модель `include/exclude/neutral`, но взаимодействие переводим на два чекбокса:
   - `Include` checked -> include;
   - `Exclude` checked -> exclude;
   - снятие чекбокса -> neutral для соответствующей оси.
3. Кнопочный UX `Include/Exclude/Clear` в C3 убираем из основного flow.

## Alternatives Considered

1. Оставить кнопки в C3 и чекбоксы в C2.
2. Перевести C2 на кнопки для симметрии.
3. Использовать единый tri-state контрол.

## Consequences

### Positive

1. Единая моторика выбора по всему Battle Workspace.
2. Более предсказуемое поведение для пользователя.
3. Проще тестировать и поддерживать frontend-контракты selection flow.

### Negative / Trade-offs

1. Требуется аккуратная синхронизация двух чекбоксов с tri-state моделью C3.
2. Нужны дополнительные UX-тесты на переключение `include/exclude/neutral`.

## Implementation Notes

1. Изменение ограничено UI-слоем C3; backend API-контракт не меняется.
2. Добавлены frontend-тесты на сохранение C3 selection при выборе через чекбоксы.
3. Документация обновляется через wiki release-note и user guide.

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
