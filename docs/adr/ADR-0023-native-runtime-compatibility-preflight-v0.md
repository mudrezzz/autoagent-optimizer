# ADR-0023: Native Runtime Compatibility Preflight v0

- Status: Accepted
- Date: 2026-05-19
- Slice: I5.S2a

## Context

После `I5.S1` выяснилось, что `run_profile --target native_runtime` может падать в процессе запуска,
если среди participants есть неподдержанные node kinds (например `hitl_gate`).

Проблема:

1. ошибка возникает поздно (в рантайме экспорта/запуска),
2. причина не агрегируется по всем participants,
3. нет структурированного preflight отчета для CI/автоматизации.

## Decision

Принято ввести обязательный preflight для `native_runtime` в режиме `strict_preflight_v0`:

1. перед native запуском строится compatibility report по каждому participant;
2. если есть несовместимые participants, native запуск блокируется;
3. CLI возвращает structured error payload:
   - `error_type=native_compatibility_preflight_failed`,
   - `preflight` report с деталями incompatibility.

## Consequences

Плюсы:

1. ошибки native target становятся предсказуемыми и explainable;
2. CI может машинно читать причину блокировки;
3. демо не “падает в середине”, а дает корректный fail-fast отчет.

Минусы:

1. пока используется только strict-поведение (без частичного выполнения).

## Follow-up

Следующий шаг — не degradation policy, а устранение несовместимости:

1. `I4.S6a`: canonical DSL->native parity для stylizer профиля (включая `hitl_gate` семантику),
2. затем `I4.S6/I4.S7`: расширение bindings и CI parity gate.
