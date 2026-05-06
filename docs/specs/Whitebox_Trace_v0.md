# Whitebox Trace v0

## Purpose

`Whitebox Trace v0` фиксирует node-level события исполнения workflow и дает базовую сводку по каждому run.

Ключевые модули:

1. [optimizer/tracing/node_events.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/tracing/node_events.py)
2. [optimizer/tracing/trace_store.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/tracing/trace_store.py)
3. [optimizer/renderer/langgraph_dai/workflow.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/workflow.py)

## Event Contract

Для каждого узла фиксируются события:

1. `started`
2. `completed`
3. `failed`
4. `skipped` (дополнительно для branch-путей)

Событие содержит:

1. `run_id`
2. `task_id`
3. `node_id`
4. `status`
5. `timestamp_utc`
6. `error` (опционально)

## Runtime Integration

1. `run_id` и `task_id` хранятся в `RenderedGraphState.task_context`.
2. Во время исполнения workflow события пишутся в `InMemoryTraceStore`.
3. Финальное состояние включает:
   - `node_events`
   - `trace_summary`

## Trace Summary Contract

`trace_summary` включает:

1. `run_id`, `task_id`
2. `events_total`
3. `nodes_touched`
4. `started`, `completed`, `failed`, `skipped`
5. `started_at_utc`, `finished_at_utc`, `duration_ms`

## CLI Visibility

Команда runtime:

```powershell
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\direct_llm.yaml --payload-file .\tmp\runtime_payload.json --pretty
```

В выводе присутствуют:

1. `node_events`
2. `trace_summary`

