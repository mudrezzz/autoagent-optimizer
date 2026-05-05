# ADR-0003: Mandatory Test Pyramid and Full Test Gate Per Slice

- Status: Accepted
- Date: 2026-05-06
- Slice: I1.S1 (quality policy hardening)
- Decision Makers: Project team
- Supersedes: N/A

## Context

Проект развивается итеративно малыми слайсами. Без строгой тестовой дисциплины
возрастает риск регрессий и потери управляемости roadmap.

Нужно формализовать обязательное требование к проверкам перед завершением каждого слайса.

## Decision

Вводится обязательная test policy:

1. Поддерживать test pyramid:
   - `unit`
   - `integration`
   - `e2e`
2. После каждого слайса выполнять полный прогон:
   - `python -m pytest`
3. Слайс не считается завершенным, пока полный прогон не зеленый.
4. При добавлении функциональности добавлять/обновлять тесты на затронутых уровнях.

## Alternatives Considered

1. Только unit-тесты.
2. Тесты только для критических релизов.
3. Ручная проверка без автоматического gate.

## Consequences

### Positive

1. Снижается риск скрытых регрессий.
2. Повышается предсказуемость итеративной разработки.
3. Ускоряется онбординг новых разработчиков за счет стабильного regression-suite.

### Negative / Trade-offs

1. Увеличивается время завершения каждого слайса.
2. Требуется постоянное сопровождение тестового контура.

## Implementation Notes

1. Добавлен `pytest.ini` с маркерами `unit/integration/e2e`.
2. Добавлены стартовые тесты текущего DSL-функционала во всех трех слоях.
3. Обновлены процессные документы (`README`, `Roadmap`, `Project_Operating_Model`).

## Verification

1. Полный локальный прогон `python -m pytest` проходит успешно.
2. Тестовые уровни запускаются и фильтруются маркерами.

## Links

1. `README.md` (Test Policy).
2. `docs/process/Project_Operating_Model.md`.
3. `Roadmap.md`.
