# ADR-0038: C5 Optimizer Setup + Guardrail Launch v0

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S7
- Decision Makers: AutoAgent Optimizer maintainers
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c5-optimizer-setup.md

## Context

После C2/C3/C4 пользователь мог собрать кандидатов, датасеты и evaluation profile,
но не было продуктового шага, где можно:

1. зафиксировать политику оптимизации (метод, область, эпохи, бюджет),
2. прогнать preflight guardrails,
3. запустить run-заявку и сохранить минимальный launch trail.

Без этого C5 оставался planned-заглушкой и разрывал основной user flow.

## Decision

Приняли C5 vertical slice v0 со следующими контрактами:

1. `GET /api/arenas/{id}/optimizer/state`
2. `POST /api/arenas/{id}/optimizer/save`
3. `POST /api/arenas/{id}/optimizer/validate`
4. `POST /api/arenas/{id}/optimizer/save-version`
5. `POST /api/arenas/{id}/optimizer/launch`

`launch` разрешается только после guardrail preflight.
Guardrails проверяют:

1. выбранные кандидаты + compile_gate ready,
2. назначенные datasets,
3. валидный C4 evaluation profile,
4. валидные поля run_plan/budget,
5. наличие хотя бы одного включенного метода.

## Alternatives Considered

1. Запускать optimizer без preflight, а ошибки разбирать в run monitor.
2. Прятать C5 до полной реализации C5/C6.
3. Делать launch только из CLI без UI.

## Consequences

### Positive

1. Закрыт end-to-end путь `C2 -> C3 -> C4 -> C5 launch` в UI.
2. Ошибки готовности ловятся до старта run, а не постфактум.
3. Появился стабильный backend-контракт для следующего слайса C5 Run Monitor.

### Negative / Trade-offs

1. Launch history пока минимальный (queue-level), без event timeline.
2. Guardrails пока rule-based, без продвинутых policy plugin-ов.

## Implementation Notes

1. `optimizer_studio` добавлен в `WorkspaceRegistryStore`.
2. C5 capability переведен в `enabled` в capability catalog.
3. Frontend добавил отдельный C5 экран с сохранением setup, validate, launch, version.
4. Launch записывается в `launch_history` (последние 20 записей).

## Verification

1. `npm run test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/unit/test_frontend_contracts.py -q`
3. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
4. `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py -q`

## Links

1. Roadmap slice: `V2.3.S7`
2. Wiki: `docs/wiki/user_guides/c5-optimizer-setup.md`
3. Release note: `docs/wiki/releases/v2.3.s7.md`
