# Graph IR v0 Specification

## Purpose

`Graph IR v0` - runtime-neutral промежуточное представление графа, на которое компилируется DSL.

Основная модель:
[optimizer/graph_ir/models.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/graph_ir/models.py)

## Core Entities

1. `GraphIRSpec`
2. `GraphIRNode`
3. `GraphIREdge`
4. `GraphNodeKind`

## Supported Node Kinds

- `llm`
- `deterministic`
- `tool`
- `validator`
- `hitl_gate`

## Required Graph Fields

1. `ir_version`
2. `entry_node`
3. `terminal_nodes`
4. `nodes`
5. `edges`

## Integrity Rules

1. `nodes[].id` уникальны.
2. `entry_node` существует среди узлов.
3. `terminal_nodes` не пустой и ссылается только на существующие узлы.
4. Каждое ребро ссылается только на существующие узлы.
5. Каждый не-терминальный узел имеет минимум одно исходящее ребро.
6. Терминальные узлы не имеют исходящих ребер.
7. Все узлы достижимы от `entry_node` (нет `unreachable nodes`).
8. Все `terminal_nodes` достижимы от `entry_node`.

## Serialization Contract

Модель поддерживает стабильный roundtrip:

1. `model_dump(mode="json")`
2. `model_dump_json()`
3. `model_validate(...)`
4. `model_validate_json(...)`

Требование v0: при roundtrip число узлов/ребер и ключевые поля не меняются.

## Reference Examples

- [examples/graph_ir/direct_llm.ir.json](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/graph_ir/direct_llm.ir.json)
- [examples/graph_ir/ocr_first.ir.json](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/graph_ir/ocr_first.ir.json)
- [examples/graph_ir/hitl_gate.ir.json](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/graph_ir/hitl_gate.ir.json)

## CLI Validation

Один файл:

```powershell
python -m optimizer.graph_ir.validate --file .\examples\graph_ir\direct_llm.ir.json --pretty
```

Smoke всех примеров:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_graph_ir.ps1
```
