# DSL v0 Specification (YAML-first)

## Purpose

DSL v0 описывает optimization-проект в декларативном виде до рендера в Graph IR/runtime.

Текущая корневая модель: `AutoAgentDslSpec` в [optimizer/dsl/schema.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/dsl/schema.py).

## Minimal Structure

Обязательные разделы:

1. `schema_version`
2. `project`
3. `mission`
4. `graph`
5. `budget`
6. `architecture_space`

Остальные разделы (`constraints`, `datasets`, `components`, `metrics`) могут быть пустыми, но для рабочих кейсов рекомендуется заполнять.

## Supported Node Types

- `llm`
- `deterministic`
- `tool`
- `validator`
- `hitl_gate`

## Validation Rules (v0)

1. `graph.nodes[].id` должны быть уникальными.
2. `graph.entry_node` должен существовать в списке узлов.
3. Все `graph.edges[].source/target` должны ссылаться на существующие узлы.
4. Каждый `graph.nodes[].component_id` должен существовать в `components[].id`.
5. Поддерживаемая версия схемы: только `"0.1"`.

## Examples

- [examples/dsl/direct_llm.yaml](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/dsl/direct_llm.yaml)
- [examples/dsl/ocr_first.yaml](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/dsl/ocr_first.yaml)
- [examples/dsl/hitl_gate.yaml](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/examples/dsl/hitl_gate.yaml)

## CLI Validation

Один файл:

```powershell
python -m optimizer.dsl.validate --file .\examples\dsl\direct_llm.yaml --pretty
```

Smoke всех примеров:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_dsl.ps1
```

Компиляция DSL в Graph IR:

```powershell
python -m optimizer.dsl.compile --dsl-file .\examples\dsl\ocr_first.yaml --output-ir-file .\tmp\ocr_first.ir.json --pretty
```
