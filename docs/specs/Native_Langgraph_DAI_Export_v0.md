# Native `langgraph-dai` Export v0

## Purpose

РЎРїРµС†РёС„РёРєР°С†РёСЏ РѕРїРёСЃС‹РІР°РµС‚ С†РµР»РµРІРѕР№ standalone export Р°РіРµРЅС‚Р°, РєРѕС‚РѕСЂС‹Р№:

1. РёСЃРїРѕР»РЅСЏРµС‚СЃСЏ РЅР° `langgraph-dai` Р±РµР· Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ РѕС‚ `optimizer.*`;
2. РїРµСЂРµРЅРѕСЃРёС‚СЃСЏ РјРµР¶РґСѓ РѕРєСЂСѓР¶РµРЅРёСЏРјРё РєР°Рє runtime-Р°СЂС‚РµС„Р°РєС‚ winner-РєРѕРЅС„РёРіСѓСЂР°С†РёРё;
3. РѕСЃС‚Р°РµС‚СЃСЏ СЃС‚СЂСѓРєС‚СѓСЂРЅРѕ СЌРєРІРёРІР°Р»РµРЅС‚РЅС‹Рј DSL/IR РёСЃРїРѕР»РЅРµРЅРёСЋ РІ optimizer.

## Scope v0

Р’ `v0` РїРѕРєСЂС‹РІР°РµРј:

1. `linear` + `conditional` workflow path;
2. node kinds:
   - `llm`,
   - `deterministic`,
   - `tool`,
   - `validator`,
   - `hitl_gate`;
3. Р±Р°Р·РѕРІС‹Р№ invoke path Рё reproducible smoke-run.

Р’РЅРµ scope v0:

1. РїРѕР»РЅС‹Р№ parity РїРѕ latency/token-cost;
2. СЃР»РѕР¶РЅС‹Рµ async/multi-tenant execution modes;
3. РґРёРЅР°РјРёС‡РµСЃРєРёРµ plugin-install flows РІ exported runtime.

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

1. Р’ exported package Р·Р°РїСЂРµС‰РµРЅС‹ РёРјРїРѕСЂС‚С‹ `optimizer.*`.
2. Р’ exported package РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ runnable entrypoint (`python -m app.run` РёР»Рё `python app/run.py`).
3. Р’СЃРµ РєСЂРёС‚РёС‡РЅС‹Рµ runtime-РєРѕРЅС„РёРіРё РґРѕР»Р¶РЅС‹ Р»РµР¶Р°С‚СЊ РІРЅСѓС‚СЂРё export package.
4. Р”Р»СЏ unresolved `python://` refs РІ v0 РґРѕРїСѓСЃРєР°РµС‚СЃСЏ explicit stub-fallback СЃ explainable РїРѕР»СЏРјРё РїСЂРёС‡РёРЅС‹.

## Mapping: Graph IR -> Native Runtime

1. `GraphIRSpec.entry_node` -> native start node.
2. `GraphIRNode(kind=llm)` -> LLM executor step СЃ prompt РёР· `prompts.yaml`.
3. `GraphIRNode(kind=deterministic/tool/validator/hitl_gate)` -> С„СѓРЅРєС†РёРё РёР· `app/nodes/*`.
4. `GraphIREdge.condition` -> native routing condition function.
5. `terminal_nodes` -> native end states.

## Parity Contract

РЎСЂР°РІРЅРёРІР°РµРј РЅРµ С‚РµРєСЃС‚ LLM-РѕС‚РІРµС‚Р°, Р° СЃС‚СЂСѓРєС‚СѓСЂРЅС‹Рµ СЃРёРіРЅР°Р»С‹:

1. executed node sequence;
2. skipped node set;
3. node output keys;
4. errors structure;
5. trace topology summary.

`text` РґРѕРїСѓСЃРєР°РµС‚ СЂР°СЃС…РѕР¶РґРµРЅРёСЏ РІ live СЂРµР¶РёРјРµ.

## Champion Bundle Integration

Champion bundle РїРѕСЃР»Рµ РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ default target РґРѕР»Р¶РµРЅ СЃРѕРґРµСЂР¶Р°С‚СЊ:

1. `native_agent/` (standalone package);
2. `parity_report.json` (`dsl_vs_native`);
3. `README.bundle.md` СЃ РѕС‚РґРµР»СЊРЅС‹РјРё С€Р°РіР°РјРё:
   - Р·Р°РїСѓСЃРє native Р°РіРµРЅС‚Р°;
   - РїСЂРѕРІРµСЂРєР° parity.

Legacy runtime export РјРѕР¶РµС‚ РѕСЃС‚Р°РІР°С‚СЊСЃСЏ РєР°Рє `legacy_agent/` С‚РѕР»СЊРєРѕ РІ debug-СЂРµР¶РёРјРµ.

## Acceptance v0

1. Native exported agent Р·Р°РїСѓСЃРєР°РµС‚СЃСЏ Р»РѕРєР°Р»СЊРЅРѕ Р±РµР· `optimizer` install.
2. Standalone smoke test РїСЂРѕС…РѕРґРёС‚.
3. Parity report РїРѕРєР°Р·С‹РІР°РµС‚ СЃС‚СЂСѓРєС‚СѓСЂРЅРѕРµ СЃРѕРѕС‚РІРµС‚СЃС‚РІРёРµ СЃ DSL path.
4. Р”РѕРєСѓРјРµРЅС‚Р°С†РёСЏ handoff РїРѕРЅСЏС‚РЅР° РЅРѕРІРѕРјСѓ СЂР°Р·СЂР°Р±РѕС‚С‡РёРєСѓ Р·Р° 10-15 РјРёРЅСѓС‚.
