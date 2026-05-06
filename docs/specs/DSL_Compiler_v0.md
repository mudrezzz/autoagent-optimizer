# DSL Compiler v0 (DSL -> Graph IR)

## Purpose

Компилятор преобразует валидный `AutoAgent DSL v0` в валидный `Graph IR v0`.

Реализация:
- [optimizer/dsl/compiler.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/dsl/compiler.py)
- [optimizer/dsl/compile_report.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/dsl/compile_report.py)
- [optimizer/dsl/compile.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/dsl/compile.py)

## Mapping Rules v0

1. `dsl.graph.entry_node` -> `ir.entry_node`
2. `dsl.graph.nodes[].id` -> `ir.nodes[].id`
3. `dsl.graph.nodes[].type` -> `ir.nodes[].kind`
4. `dsl.component[component_id].implementation` -> `ir.nodes[].component_ref`
5. `dsl.graph.nodes[].prompt_id` -> `ir.nodes[].config.prompt_id`
6. `dsl.graph.edges[]` -> `ir.edges[]`
7. `ir.terminal_nodes` вычисляются как узлы без исходящих ребер

## Compile Report

Отчет включает:

1. `status`: `success|failure`
2. `node_mappings`: таблица соответствий DSL <-> IR
3. `issues`: предупреждения/ошибки

## CLI

Компиляция одного файла:

```powershell
python -m optimizer.dsl.compile --dsl-file .\examples\dsl\ocr_first.yaml --output-ir-file .\tmp\ocr_first.ir.json --pretty
```

Smoke компиляции всех примеров:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_compile_dsl_to_ir.ps1
```
