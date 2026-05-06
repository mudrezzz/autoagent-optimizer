# Agent Codegen v0

## Purpose

`Agent Codegen v0` добавляет путь материализации найденной конфигурации в исполняемый Python-код, чтобы лучшую DSL/IR-конфигурацию можно было сразу брать в разработку и эксплуатацию.

Основные модули:

1. [optimizer/codegen/agent_generator.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/codegen/agent_generator.py)
2. [optimizer/codegen/generate.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/codegen/generate.py)
3. [scripts/smoke_generate_agent_code.ps1](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/scripts/smoke_generate_agent_code.ps1)

## Source Inputs

Генератор поддерживает два входа:

1. DSL YAML (`--dsl-file`) с автоматической компиляцией в Graph IR.
2. Graph IR JSON (`--graph-ir-file`) без промежуточной компиляции.

## Generated Artifact Layout

```text
<output_dir>/
  <package_name>/
    __init__.py
    graph_ir.json
    bindings.py
    agent.py
  run_generated_agent.py
  README.generated.md
```

## Runtime Semantics

1. `graph_ir.json` фиксирует итоговую runtime-neutral спецификацию.
2. `agent.py` поднимает `GraphIRToLangGraphRenderer` и запускает workflow через `invoke`.
3. `bindings.py` строит `RendererBindings`:
   - prompt templates создаются как TODO-шаблоны по `prompt_id`;
   - для `python://module:function` используется ленивый импорт;
   - если callable недоступен, применяется fallback.
4. Fallback-поведение v0:
   - `deterministic|tool`: stub-ответ;
   - `validator`: `{"valid": true}`;
   - `hitl_gate`: решение из `payload.review_decision` или `approve`.

## CLI

```powershell
python -m optimizer.codegen.generate --dsl-file .\examples\dsl\direct_llm.yaml --output-dir .\tmp\demo_codegen --package-name support_agent_v1 --pretty
```

## Demo

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_agent_code.ps1
```

Ожидаемый результат:

1. Сгенерирован пакет агента в `tmp/generated_agent_demo`.
2. Выполнен запуск `run_generated_agent.py`.
3. В консоли виден JSON с `executed_nodes`, `node_outputs`, `trace`.

