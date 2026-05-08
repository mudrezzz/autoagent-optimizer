# ADR-0020: Native Exporter Minimal v0 and Fallback Policy

- Status: Accepted
- Date: 2026-05-08
- Slice: I4.S5
- Decision Makers: Project team
- Supersedes: N/A

## Context

После фиксации стратегии standalone native export (`ADR-0019`) нужен первый исполняемый инкремент,
который можно запускать уже сейчас на реальном demo-кейсе.

Ограничения текущего этапа:

1. Нельзя сразу покрыть все node kinds и все вариации component bindings.
2. Нужно избежать падения demo из-за отсутствующих `python://` модулей в новом standalone пакете.
3. При этом необходимо сохранить прозрачность поведения и диагностируемость.

## Decision

Вводим `Native Exporter Minimal v0`:

1. Поддерживаем в v0 только node kinds:
   - `llm`,
   - `deterministic`,
   - `validator`.
2. Для `tool` и `hitl_gate` exporter делает fail-fast на этапе экспорта.
3. Для `python://` refs внутри `deterministic`/`validator`:
   - если callable резолвится, выполняем его;
   - если не резолвится, используем явный stub-результат с полями `reason=python_callable_unresolved`.
4. Champion bundle включает `native_agent/` и runtime smoke-check standalone запуска.

## Alternatives Considered

1. Сразу поддержать все node kinds в I4.S5.
2. Фейлить экспорт при любом unresolved `python://` ref.
3. Не запускать native runtime в bundle smoke, ограничиться только генерацией файлов.

## Consequences

### Positive

1. Получен первый runnable standalone runtime артефакт без `optimizer.*` импортов.
2. Demo можно запускать end-to-end уже на этом слайсе.
3. Проблемы unresolved refs видны явно в payload/trace, а не маскируются молча.

### Negative / Trade-offs

1. Покрытие node kinds неполное до I4.S6.
2. Stub-policy может временно упрощать бизнес-логику до полной реализации bindings.
3. Нужен follow-up слайс для строгих binding-контрактов и расширения поддержки.

## Implementation Notes

1. Добавлен модуль `optimizer/champion/native_export.py`.
2. `optimizer/champion/export_bundle.py` теперь формирует `native_agent/` и `native_runtime_smoke` в parity report.
3. Обновлен smoke script champion bundle с реальным запуском standalone native runner.
4. Добавлены unit/integration проверки native export path.

## Verification

1. `python -m pytest` green.
2. `native_agent/app/run.py` запускается из экспортированного bundle.
3. В `parity_report.json` поле `native_runtime_smoke.passed=true`.
4. В generated native source нет импортов `optimizer.*`.

## Links

1. `optimizer/champion/native_export.py`
2. `docs/specs/Native_Langgraph_DAI_Export_v0.md`
3. `docs/specs/Champion_Export_Bundle_v0.md`

