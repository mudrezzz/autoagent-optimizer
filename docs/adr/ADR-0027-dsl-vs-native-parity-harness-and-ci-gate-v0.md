# ADR-0027: DSL-vs-Native Parity Harness and CI Gate v0

- Status: Accepted
- Date: 2026-05-21
- Slice: I4.S7

## Context

После закрытия `I4.S6` покрытие node kinds в native runtime стало полным, но отсутствовал единый автоматический gate,
который подтверждает, что DSL path и native path остаются эквивалентными по структуре исполнения.

Без этого:

1. возможен скрытый drift в ветвлениях/ошибках/форме outputs;
2. регрессии выявляются поздно, вручную;
3. CI не имеет формального критерия parity.

## Decision

Принято добавить отдельный parity-контур:

1. модуль `optimizer.parity` с CLI `python -m optimizer.parity.run`;
2. структурный comparator по сигналам:
   - `executed_nodes`,
   - `skipped_nodes`,
   - `node_output_keys`,
   - `errors`,
   - `trace_topology`;
3. `--fail-on-mismatch` как CI-gate режим (exit code `1` при mismatch);
4. smoke/e2e сценарий parity в стандартном наборе регрессионных прогонов.

## Consequences

Плюсы:

1. формальный критерий DSL==Native parity в CI;
2. drift выявляется рано и локализуется по конкретным structural checks;
3. независимость от LLM-текстовой вариативности за счет mock-LLM режима.

Ограничения:

1. parity v0 проверяет structural, а не semantic text equivalence;
2. для глубокого quality сравнения остаются evaluation/evidence контуры.

## Follow-up

Следующий шаг: `I4.S8` — native-first champion bundle default switch.

