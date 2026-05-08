# Native `langgraph-dai` Export v0

## Purpose

Спецификация описывает целевой standalone export агента, который:

1. исполняется на `langgraph-dai` без зависимостей от `optimizer.*`;
2. переносится между окружениями как runtime-артефакт winner-конфигурации;
3. остается структурно эквивалентным DSL/IR исполнению в optimizer.

## Scope v0

В `v0` покрываем:

1. `linear` + `conditional` workflow path;
2. node kinds:
   - `llm`,
   - `deterministic`,
   - `validator`;
3. базовый invoke path и reproducible smoke-run.

Вне scope v0:

1. полный parity по latency/token-cost;
2. сложные async/multi-tenant execution modes;
3. динамические plugin-install flows в exported runtime.
4. node kinds `tool` и `hitl_gate` (будут добавлены в I4.S6).

## Export Package Contract

```text
<export_root>/
  README.md
  requirements.txt
  pyproject.toml (optional v0)
  config/
    workflow.yaml
    runtime.yaml
  prompts/
    prompts.yaml
  app/
    workflow.py
    bindings.py
    nodes/
      deterministic.py
      validators.py
      tools.py
      hitl.py
    run.py
  artifacts/
    source_graph_ir.json
    export_manifest.json
```

## Hard Constraints

1. В exported package запрещены импорты `optimizer.*`.
2. В exported package должен быть runnable entrypoint (`python -m app.run` или `python app/run.py`).
3. Все критичные runtime-конфиги должны лежать внутри export package.
4. Для unresolved `python://` refs в v0 допускается explicit stub-fallback с explainable полями причины.

## Mapping: Graph IR -> Native Runtime

1. `GraphIRSpec.entry_node` -> native start node.
2. `GraphIRNode(kind=llm)` -> LLM executor step с prompt из `prompts.yaml`.
3. `GraphIRNode(kind=deterministic/tool/validator/hitl_gate)` -> функции из `app/nodes/*`.
4. `GraphIREdge.condition` -> native routing condition function.
5. `terminal_nodes` -> native end states.

## Parity Contract

Сравниваем не текст LLM-ответа, а структурные сигналы:

1. executed node sequence;
2. skipped node set;
3. node output keys;
4. errors structure;
5. trace topology summary.

`text` допускает расхождения в live режиме.

## Champion Bundle Integration

Champion bundle после переключения default target должен содержать:

1. `native_agent/` (standalone package);
2. `parity_report.json` (`dsl_vs_native`);
3. `README.bundle.md` с отдельными шагами:
   - запуск native агента;
   - проверка parity.

Legacy runtime export может оставаться как `legacy_agent/` только в debug-режиме.

## Acceptance v0

1. Native exported agent запускается локально без `optimizer` install.
2. Standalone smoke test проходит.
3. Parity report показывает структурное соответствие с DSL path.
4. Документация handoff понятна новому разработчику за 10-15 минут.
