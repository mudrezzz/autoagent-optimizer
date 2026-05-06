# ADR-0009: Node Event Capture and Trace Summary v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I2.S3
- Decision Makers: Project team
- Supersedes: N/A

## Context

После запуска runtime-path в I2.S1-I2.S2 не хватало диагностической прозрачности:
было видно финальное состояние, но не было строгого контракта node-level событий и сводки по run.

Для белого ящика нужны:

1. события `started/completed/failed` на уровне узла;
2. привязка к `run_id/task_id`;
3. агрегированная summary для быстрых проверок.

## Decision

Принять `Whitebox Trace v0`:

1. Ввести структурированное событие `NodeExecutionEvent`.
2. Добавить `InMemoryTraceStore` как хранилище и агрегатор сводки.
3. Интегрировать запись событий в runtime workflow.
4. Пробрасывать `node_events` и `trace_summary` в финальный state/CLI-вывод.

## Alternatives Considered

1. Логировать только текстовые сообщения без структурированного контракта.
2. Писать события сразу во внешнее persistent хранилище.
3. Отложить tracing до итераций evaluation/evidence.

## Consequences

### Positive

1. Появилась проверяемая node-level трассировка в каждом run.
2. CLI теперь дает диагностику по ходу исполнения, а не только финальный payload.
3. Создана основа для следующих шагов метрик/evidence.

### Negative / Trade-offs

1. Trace store v0 in-memory и не сохраняет историю между процессами.
2. События пока ограничены базовым набором и не включают детальную latency по узлу.
3. Для production потребуется расширение в persistent storage.

## Implementation Notes

1. Добавлены:
   - `optimizer/tracing/node_events.py`,
   - `optimizer/tracing/trace_store.py`.
2. Обновлены:
   - `optimizer/renderer/langgraph_dai/runtime_state.py`,
   - `optimizer/renderer/langgraph_dai/workflow.py`,
   - `optimizer/renderer/langgraph_dai/run.py`,
   - `optimizer/renderer/langgraph_dai/adapter.py`.
3. Добавлена спецификация `docs/specs/Whitebox_Trace_v0.md`.

## Verification

1. Unit: trace store summary.
2. Integration: runtime и CLI возвращают `node_events` + `trace_summary`.
3. Полный `python -m pytest` зеленый после слайса.

## Links

1. `docs/specs/Whitebox_Trace_v0.md`
2. `Roadmap.md` (I2.S3)
3. `docs/demo/Demo_Track.md`

