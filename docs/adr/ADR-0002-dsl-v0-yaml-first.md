# ADR-0002: DSL v0 Uses YAML-First Format

- Status: Accepted
- Date: 2026-05-06
- Slice: I1.S1
- Decision Makers: Project team
- Supersedes: N/A

## Context

Для быстрого старта MVP требуется декларативный формат, который:

1. легко читать и редактировать вручную;
2. удобен для ревью в git;
3. позволяет валидировать схему через typed contracts.

На этом этапе важно минимизировать порог входа и быстро итерировать структуру DSL.

## Decision

В DSL v0 выбираем YAML-first подход:

1. пользовательский исходник хранится в `.yaml`;
2. валидация выполняется через `pydantic`-модель `AutoAgentDslSpec`;
3. CLI-валидация доступна через `python -m optimizer.dsl.validate`.

Python SDK-first откладывается на следующий этап после стабилизации DSL/IR boundary.

## Alternatives Considered

1. Python SDK-first.
2. JSON-only DSL.
3. Гибрид YAML+Python в рамках одного слайса.

## Consequences

### Positive

1. Быстрый вход для разработчиков и архитекторов.
2. Прозрачный diff/review для изменений спецификаций.
3. Простой smoke-path для автоматической валидации.

### Negative / Trade-offs

1. Нет compile-time подсказок как в Python SDK.
2. Потребуется дополнительный слой, если позже добавим программный DSL-builder.
3. Возможны ошибки форматирования YAML, требующие отдельной диагностики.

## Implementation Notes

1. Реализованы `optimizer.dsl.schema`, `optimizer.dsl.io`, `optimizer.dsl.validate`.
2. Добавлены эталонные файлы в `examples/dsl`.
3. Добавлен smoke-скрипт `scripts/smoke_validate_dsl.ps1`.

## Verification

1. Валидация трех сценариев (`direct_llm`, `ocr_first`, `hitl_gate`) проходит успешно.
2. При ошибках CLI возвращает non-zero код.

## Links

1. `Roadmap.md` (I1.S1).
2. `docs/specs/DSL_v0.md`.
3. `docs/backlog/Executable_Slice_Backlog.md`.
