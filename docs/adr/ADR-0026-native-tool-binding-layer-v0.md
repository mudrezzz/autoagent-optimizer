# ADR-0026: Native Tool Binding Layer v0 for DSL==Native Coverage

- Status: Accepted
- Date: 2026-05-21
- Slice: I4.S6

## Context

После закрытия `I4.S6a` canonical stylizer путь на native работал, но `tool`-узлы оставались последним системным разрывом между `dsl_runtime` и `native_runtime`.

Следствие:

1. profile-run с `tool`-кандидатами требовал preflight-блокировки по node kind;
2. native coverage по node kinds была неполной;
3. parity-путь для mixed pipelines (LLM + tool + deterministic + validator + HITL) оставался незакрытым.

## Decision

Принято расширить native exporter/runtime до полноценного `tool` binding слоя v0:

1. `tool` включен в supported node kinds native exporter и preflight capability matrix;
2. для `python://module:function` добавлен прямой callable path в native runtime;
3. для `mcp://...` добавлен явный наблюдаемый `mcp_stub` контракт (не silent fallback), чтобы поведение было диагностируемым;
4. ошибки unresolved bindings остаются explainable и видимыми в runtime/preflight контуре.

## Consequences

Плюсы:

1. закрыт полный набор node kinds v0: `llm`, `deterministic`, `tool`, `validator`, `hitl_gate`;
2. профили с `tool`-узлами больше не блокируются preflight-ом только из-за node kind;
3. демо и тесты отражают единый target path без workaround-политик.

Ограничения:

1. `mcp://` path в v0 остается stub-механикой до следующего шага полной MCP-интеграции;
2. содержательная semantic parity оценивается далее через `I4.S7` structural parity harness + CI gate.

## Follow-up

1. `I4.S7`: автоматизированный DSL-vs-native parity harness + CI gate;
2. `I4.S8`: native-first champion bundle default switch.
