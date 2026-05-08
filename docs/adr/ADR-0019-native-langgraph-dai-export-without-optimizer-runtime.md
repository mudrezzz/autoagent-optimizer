# ADR-0019: Native `langgraph-dai` Export Without Optimizer Runtime

- Status: Accepted
- Date: 2026-05-08
- Slice: I4.S4 (design)
- Decision Makers: Project team
- Supersedes: ADR-0018 (частично, в части runtime-зависимости экспортируемого агента)

## Context

Текущий champion export bundle генерирует код, который в runtime остается зависим от `optimizer.*`.
Это не решает задачу реального handoff в прод:

1. экспортируемый агент остается на том же runtime-контуре, что и control plane;
2. фактически сохраняется vendor lock на внутренние модули optimizer;
3. нет гарантии, что команда сможет запускать агента как самостоятельный `langgraph-dai` проект.

## Decision

Принимаем архитектурный разворот:

1. `optimizer` остается только control plane (search/eval/arena/evidence/export orchestration).
2. Экспортируемый агент должен быть standalone пакетом на `langgraph-dai` без импортов `optimizer.*`.
3. Вводим новый export target:
   - `langgraph_dai_native`.
4. Champion bundle по умолчанию должен экспортировать native-агента, а legacy-runtime путь оставить только как fallback/debug режим.
5. Эквивалентность `DSL path` vs `native exported path` подтверждается parity-гейтом по структурным сигналам выполнения.

## Alternatives Considered

1. Оставить текущий runtime-зависимый export и усилить только README/паритет.
2. Экспортировать только конфиг/IR без runnable native-кода.
3. Делать одноразовый ручной перенос в `langgraph-dai` для каждого winner.

## Consequences

### Positive

1. Реально снимается runtime/vendor lock на optimizer.
2. Winner-артефакт становится переносимым и пригодным для независимой эксплуатации.
3. Граница `control plane` vs `runtime artifact` становится явной и технически проверяемой.

### Negative / Trade-offs

1. Увеличивается объем codegen-логики и тестового контура.
2. Появляется риск drift между internal renderer и native export path.
3. Нужен отдельный parity-harness и regression-поддержка mapping-правил.

## Implementation Notes

Реализация идет отдельными слайсами:

1. Контракт native export пакета и mapping таблица `Graph IR -> langgraph-dai`.
2. Minimal native renderer/codegen (`linear + branch`).
3. Component binding layer для `llm/deterministic/tool/validator/hitl`.
4. Standalone parity-gate и smoke-path без `optimizer` импорта.
5. Переключение champion bundle default на native target.

## Verification

1. Exported package запускается в чистом окружении без установки `optimizer`.
2. `rg "optimizer\."` по exported package возвращает 0 совпадений.
3. Parity gate подтверждает структурную эквивалентность выполнения.
4. Champion bundle содержит developer README с standalone quickstart.

## Links

1. `docs/specs/Native_Langgraph_DAI_Export_v0.md`
2. `Roadmap.md` (`I4.S4`-`I4.S8`)
3. `docs/backlog/Executable_Slice_Backlog.md`

