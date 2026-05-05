# ADR-0004: Graph IR v0 as Runtime-Neutral Boundary

- Status: Accepted
- Date: 2026-05-06
- Slice: I1.S2
- Decision Makers: Project team
- Supersedes: N/A

## Context

После появления DSL v0 нужен промежуточный слой между DSL и runtime-рендерером.
Без такого слоя:

1. DSL начинает протекать runtime-деталями;
2. сложнее поддерживать несколько render targets в будущем;
3. возрастает связанность и риск изменений.

## Decision

Вводим `Graph IR v0` как обязательную runtime-neutral границу:

1. DSL компилируется сначала в Graph IR.
2. Рендереры (LangGraph и будущие targets) работают только с Graph IR.
3. В Graph IR фиксируем строгие проверки:
   - start/end корректность;
   - валидность ребер;
   - отсутствие unreachable узлов;
   - сериализационный roundtrip без потери структуры.

## Alternatives Considered

1. Рендерить DSL напрямую в runtime.
2. Хранить только runtime-специфичный graph object.
3. Строить IR в неявном виде без typed-схемы.

## Consequences

### Positive

1. Чистое разделение этапов `DSL -> IR -> Renderer`.
2. Стабильная точка расширения для будущих runtime targets.
3. Упрощение тестирования и диагностики графовой структуры.

### Negative / Trade-offs

1. Дополнительный слой моделей и валидаторов.
2. Появляется этап компиляции DSL->IR, который тоже нужно поддерживать.

## Implementation Notes

1. Добавлены `optimizer.graph_ir.models`, `optimizer.graph_ir.validators`, `optimizer.graph_ir.validate`.
2. Добавлены референсные примеры `examples/graph_ir/*.json`.
3. Добавлены unit/integration/e2e тесты и smoke-скрипт.

## Verification

1. Полный `python -m pytest` проходит успешно.
2. Отдельные smoke-команды DSL и Graph IR проходят успешно.

## Links

1. `docs/specs/GraphIR_v0.md`
2. `Roadmap.md` (I1.S2)
3. `docs/backlog/Executable_Slice_Backlog.md`
