# ADR-0036: C4 UX Unification and Dedicated Dataset Editor

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S5a
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c4-dataset-studio.md

## Context

После V2.3.S5 C4 функционально работал, но UX отличался от C2/C3:

1. Dataset-операции были в форме/таблице, а не в кандидат-подобном списке.
2. Не было единого выбора dataset-ов через чекбоксы + явный Save.
3. Не было отдельного editor-экрана для детальной правки конкретного dataset.

Из-за этого нарушалось правило UX-единообразия в Battle Workspace.

## Decision

1. Привести C4 список dataset-ов к визуальному и поведенческому паттерну C2/C3:
   - row list,
   - checkbox selection,
   - явная кнопка `Save`.
2. Добавить multi-dataset assignment для арены через новый endpoint:
   - `POST /api/arenas/{arena_id}/datasets/assign`.
3. Добавить details-accordion в списке dataset-ов с preview первых 5 строк.
4. Добавить отдельный C4 editor-screen c breadcrumbs для работы с одним dataset:
   - редактирование строк,
   - удаление строк,
   - импорт JSONL в editor,
   - сохранение изменений через replace,
   - validate/save version внутри editor.

## Alternatives Considered

1. Оставить форму и таблицу внутри одного экрана без выделенного editor-режима.
2. Делать назначение dataset-ов автоматически без явного Save.
3. Вынести editor в отдельный route сразу (без промежуточного in-panel screen).

## Consequences

### Positive

1. C2/C3/C4 используют единый UX-паттерн выбора сущностей.
2. Пользователь получает быстрый обзор dataset-ов и отдельный фокусный экран для глубокого редактирования.
3. Multi-dataset assignment теперь явный, воспроизводимый и доступен для будущего C5 run setup.

### Negative / Trade-offs

1. Состояние C4 на frontend стало сложнее (`list/edit`, dirty selection, editor rows).
2. Добавился новый API-контракт assignment, который нужно поддерживать дальше.

## Implementation Notes

1. Store: `dataset_studio` расширен полем `assigned_dataset_ids`.
2. API: state payload включает `assigned_dataset_ids` и `preview_rows`; добавлен `/datasets/assign`.
3. Frontend: C4 render split на `list` и `edit` режимы с breadcrumbs.
4. QA: обновлены frontend unit, backend integration и smoke e2e сценарии.

## Verification

1. `npm run test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/unit/test_frontend_contracts.py -q`
3. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
4. `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py -q`

## Links

1. `Roadmap.md` (`V2.3.S5a`)
2. `frontend/src/App.tsx`
3. `optimizer/frontend/dev_server.py`
4. `optimizer/workspace/registry_store.py`
5. `docs/wiki/releases/v2.3.s5a.md`
