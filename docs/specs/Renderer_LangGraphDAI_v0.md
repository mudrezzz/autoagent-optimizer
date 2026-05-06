# Renderer LangGraph-DAI v0

## Purpose

Рендерер превращает `Graph IR v0` в исполняемый workflow на базе `langgraph-dai` (`BaseWorkflow`).

Ключевые модули:

1. [adapter.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/adapter.py)
2. [workflow.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/workflow.py)
3. [node_executor.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/node_executor.py)
4. [condition_eval.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/condition_eval.py)
5. [run.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/run.py)

## Runtime Model

1. Graph IR валидируется и топологически упорядочивается.
2. Для каждого узла строится `WorkflowNodeSpec`.
3. В runtime ведется `RenderedGraphState`:
   - `active_nodes`
   - `executed_nodes`
   - `skipped_nodes`
   - `node_outputs`
   - `trace`
   - `node_events`
   - `trace_summary`
4. Условные ребра оцениваются через `ConditionEvaluator`.

## Branch Semantics v0

1. Если условие ребра истинно, целевой узел активируется.
2. Неактивный узел помечается как `skipped`.
3. `terminal_nodes` завершают ветку и не должны иметь исходящих ребер.

## Node Execution v0

1. `llm`:
   - при наличии `OPENROUTER_API_KEY` выполняется реальный вызов OpenRouter;
   - без ключа используется mock-режим `[mock-llm] ...`.
2. `deterministic|tool|validator|hitl_gate`:
   - через registry;
   - или `python://module:function`;
   - `tool` с `mcp://` пока работает как stub.

## Failure Policy v0

1. `stop`: ошибка пробрасывается и прерывает workflow.
2. `retry`: одна повторная попытка.
3. `fallback`: ошибка фиксируется в state и узел возвращает fallback-output.

## CLI Demo

Запуск через DSL:

```powershell
New-Item -ItemType Directory -Force -Path .\tmp | Out-Null
'{"query":"Summarize project goal"}' | Set-Content -LiteralPath .\tmp\runtime_payload.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\direct_llm.yaml --payload-file .\tmp\runtime_payload.json --pretty
```

Smoke runtime demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
```

Примечание: для PowerShell основной способ запуска — `--payload-file`, чтобы избежать ошибок экранирования JSON.

Resume запуск из checkpoint:

```powershell
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --resume-task-id demo-resume-task --payload-file .\tmp\resume.json --checkpoint-dir .\tmp\runtime_checkpoints --pretty
```
