# ADR-0006: DSL to Graph IR Mapping v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I1.S3
- Decision Makers: Project team
- Supersedes: N/A

## Context

После внедрения DSL и Graph IR нужен детерминированный и повторяемый mapping.
Без явных правил mapping:

1. рендер может стать непредсказуемым;
2. тестировать компиляцию сложно;
3. появится риск несовместимости между слайсами.

## Decision

Фиксируем компилятор `DSL -> Graph IR` с явными правилами v0:

1. Graph structure переносится 1-к-1 (entry/nodes/edges).
2. Node kind маппится напрямую (`llm|deterministic|tool|validator|hitl_gate`).
3. `component_id` резолвится в `component_ref` по `components[].implementation`.
4. `terminal_nodes` вычисляются как узлы без исходящих ребер.
5. На выходе всегда формируется compile report с node mapping и issues.

## Alternatives Considered

1. Генерировать IR с неявными fallback-правилами.
2. Делать compile без отчета.
3. Откладывать компилятор и рендерить DSL напрямую.

## Consequences

### Positive

1. Прозрачный и тестируемый compile path.
2. Упрощенная диагностика ошибок через compile report.
3. Готовая граница для следующего слайса `I2.S1` (renderer).

### Negative / Trade-offs

1. Дополнительный код/тесты и сопровождение mapping-правил.
2. В v0 ограниченная гибкость (минимальная трансформация).

## Implementation Notes

1. Реализованы `optimizer.dsl.compiler`, `optimizer.dsl.compile_report`, `optimizer.dsl.compile`.
2. Добавлен smoke-скрипт `scripts/smoke_compile_dsl_to_ir.ps1`.
3. Добавлены unit/integration/e2e тесты компилятора.

## Verification

1. Все референсные DSL-компилируются в валидный Graph IR.
2. Полный `python -m pytest` проходит.

## Links

1. `docs/specs/DSL_Compiler_v0.md`
2. `docs/specs/DSL_v0.md`
3. `docs/specs/GraphIR_v0.md`
