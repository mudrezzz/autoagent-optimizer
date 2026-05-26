# ADR-0037: C4 Metrics & Evaluators Studio v0

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S6
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/c4-dataset-studio.md

## Context

После C4 dataset flow пользователю всё ещё не хватало UI-контроля над логикой оценки:

1. Метрики сравнений и диагностик были фиксированы.
2. Набор evaluators нельзя было конфигурировать через продуктовый интерфейс.
3. Бюджет evaluation profile не имел отдельного контрактного слоя в C4.

Нужен вертикальный слайс, который делает evaluation profile управляемым из UI и проверяемым через API.

## Decision

1. Добавить в arena-state отдельный `evaluation_studio` блок.
2. Ввести C4 API-контуры:
   - `GET /api/arenas/{id}/evaluation/state`
   - `POST /api/arenas/{id}/evaluation/metrics/save`
   - `POST /api/arenas/{id}/evaluation/evaluators/save`
   - `POST /api/arenas/{id}/evaluation/budget/save`
   - `POST /api/arenas/{id}/evaluation/validate`
   - `POST /api/arenas/{id}/evaluation/save-version`
3. Разделить профиль на явные сущности:
   - `comparative_metrics`
   - `diagnostic_signals`
   - `evaluators`
   - `budget`
   - `versions`
4. Добавить validate-правила v0 и version snapshot evaluation profile.

## Alternatives Considered

1. Оставить evaluation config в backend-only YAML без UI.
2. Сохранить только один merged список метрик без разделения comparative/diagnostic.
3. Не вводить версионирование profile до C5.

## Consequences

### Positive

1. C4 теперь покрывает и данные, и профиль оценки в едином capability.
2. Пользователь может итеративно подбирать метрики/evaluators/бюджет под конкретный кейс.
3. Валидация и versioning снижает риск запусков с некорректным профилем.

### Negative / Trade-offs

1. Состояние frontend/backend стало шире и сложнее.
2. Validate v0 остаётся базовым и не заменяет глубокие доменные проверки.

## Implementation Notes

1. Store расширен `evaluation_studio` с нормализаторами и методами save/validate/version.
2. Dev server получил отдельные C4 evaluation handlers.
3. UI C4 дополнился панелью `Metrics & Evaluators Studio`.
4. Targeted gate расширен интеграционными/e2e шагами для evaluation endpoints.

## Verification

1. `npm run test -- --run src/__tests__/app.workspace.test.tsx`
2. `python -m pytest tests/unit/test_frontend_contracts.py -q`
3. `python -m pytest tests/integration/test_frontend_dev_server.py -q`
4. `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py -q`

## Links

1. `Roadmap.md` (`V2.3.S6`)
2. `optimizer/workspace/registry_store.py`
3. `optimizer/frontend/dev_server.py`
4. `frontend/src/App.tsx`
5. `docs/wiki/releases/v2.3.s6.md`
