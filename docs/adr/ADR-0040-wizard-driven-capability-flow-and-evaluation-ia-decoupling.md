# ADR-0040: Wizard-Driven Capability Flow and Evaluation IA Decoupling

- Status: Accepted
- Date: 2026-05-27
- Slice: V2.4.S1-V2.4.S7 (planning baseline)
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/user_guides/overview.md

## Context

Текущий UX смешивает в одном контуре несколько независимых задач:

1. Dataset lifecycle,
2. Metrics definition,
3. Evaluator strategy.

Также левое меню работает как обычная навигация, хотя фактически продукт требует последовательный процесс с зависимостями шагов.
Это приводит к двум проблемам:

1. пользователь может зайти в шаг, который еще не имеет корректных входных данных;
2. логика оценки агентов (особенно для разных архитектурных типов) остается неявной и частично захардкоженной.

## Decision

1. Левое меню `Battle Workspace` переводится в stateful wizard-модель.
2. `Datasets`, `Metrics`, `Evaluators` оформляются как отдельные capability-пункты.
3. Метрики становятся candidate-feature-aware:
   - comparative-метрики доступны только когда релевантны выбранным candidate-архитектурам.
4. Evaluators конфигурируются отдельно и связываются с метриками через матрицу `Evaluator x Metric`.
5. Dataset-контракт расширяется до stage-aware модели (`retrieval/rerank/synthesis/final`), а не только `input/final output`.
6. Правый чат становится контекстным: его автоматизации зависят от активной capability-вкладки.
7. `Runtime snapshot` убирается из основного пользовательского полотна в debug-surface.

## Alternatives Considered

1. Оставить `Dataset + Metrics + Evaluators` объединенными в одном capability-экране.
2. Добавить только визуальные улучшения без wizard-gating модели.
3. Жестко хардкодить список метрик независимо от candidate-features.

## Consequences

### Positive

1. Пользовательский flow становится линейным и объяснимым.
2. Снижается когнитивная нагрузка на шагах оценки.
3. Логика оценки становится расширяемой и совместимой с разными типами задач.
4. Улучшается готовность к сценариям без golden dataset (например, pure LLM-as-judge).

### Negative / Trade-offs

1. Увеличивается сложность оркестрации UI-состояний и preflight-проверок.
2. Потребуется миграция capability-ярлыков и части контрактов API/UI.
3. Понадобится расширение тестового контура (wizard, matrix, stage-aware dataset).

## Implementation Notes

Серия слайсов `V2.4.*` реализует решение по частям:

1. `V2.4.S1` Wizard Engine v0,
2. `V2.4.S2` IA split (C4/C5/C6),
3. `V2.4.S3` feature-aware metrics,
4. `V2.4.S4` evaluator x metric matrix,
5. `V2.4.S5` dataset v2 schema,
6. `V2.4.S6` contextual chat per capability,
7. `V2.4.S7` runtime snapshot UX cleanup.

## Verification

1. UI-гейтинг шагов проверяется integration/e2e тестами.
2. Невозможен `optimizer launch`, если wizard prerequisites не выполнены.
3. Для каждой comparative-метрики есть evaluator coverage в matrix preflight.
4. Stage-aware dataset сценарии валидируются unit/integration тестами.

## Links

1. `Roadmap.md` (V2.4 section)
2. `System_Architecture_Overview.md`
3. `docs/specs/Frontend_Architecture_v0.md`
