# ADR-0039: C4 UX Split into Dataset and Metrics Tabs

- Status: Accepted
- Date: 2026-05-27
- Slice: V2.3.S6a
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c4-dataset-studio.md

## Context

В C4 dataset-поток и metrics-поток были смешаны в одном экране.
Это ухудшало UX: пользователь видел одновременно две разные задачи (подготовка датасета и настройка evaluation profile),
что снижало читаемость и усложняло навигацию.

## Decision

1. C4 делится на две явные вкладки: `Datasets` и `Metrics`.
2. Во вкладке `Datasets` остаются только операции жизненного цикла dataset.
3. Во вкладке `Metrics` остаются только операции evaluation profile:
   - comparative metrics,
   - diagnostic signals,
   - evaluators,
   - budget,
   - validate/save version.
4. Backend-контракт C4 сохраняется обратно совместимым (legacy mirror fields), чтобы не ломать текущие API и тесты.

## Alternatives Considered

1. Оставить единый экран без табов.
2. Вынести metrics в отдельную capability (новый пункт левого меню).
3. Перевести C4 сразу на мульти-profile UI без промежуточного UX-шага.

## Consequences

### Positive

1. Пользовательский поток C4 становится линейным и предсказуемым.
2. Снижается когнитивная нагрузка в C4.
3. Проще покрывать UI тестами отдельные сценарии `datasets` и `metrics`.

### Negative / Trade-offs

1. Добавляется дополнительный click для перехода к metrics-настройке.
2. Требуется поддерживать состояние активной вкладки в UI.

## Implementation Notes

1. Frontend: `frontend/src/App.tsx`, `frontend/styles.css`.
2. Tests: `frontend/src/__tests__/app.workspace.test.tsx`.
3. Backend consistency: `optimizer/workspace/registry_store.py`.
4. Документация обновляется с реальными UI-скриншотами в wiki.

## Verification

1. `npm --prefix frontend test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
3. `python -m pytest tests/unit/test_workspace_registry_store.py -q`

## Links

1. `Roadmap.md` (V2.3.S6a)
2. `docs/wiki/releases/v2.3.s6a.md`
3. `docs/wiki/user_guides/c4-dataset-studio.md`
