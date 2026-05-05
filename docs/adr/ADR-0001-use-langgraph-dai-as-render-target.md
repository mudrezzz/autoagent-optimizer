# ADR-0001: Use `langgraph-dai` as the First Render Target

- Status: Accepted
- Date: 2026-05-06
- Slice: I0.S1
- Decision Makers: Project team
- Supersedes: N/A

## Context

AutoAgent Optimizer требует раннего исполняемого runtime для цикла:
`DSL -> IR -> execution -> white-box evaluation`.

Нужен OSS-first путь с:

1. LangGraph-compatible workflow model.
2. invoke/resume support.
3. node-level event hooks.
4. typed contracts и extension playbooks.

В проект уже добавлен `langgraph-document-ai-platform`, где есть library mode (`langgraph-dai`) с `framework`, `schemas`, `infra.openrouter`.

## Decision

На MVP-1 использовать `langgraph-dai` как первый render target.

Правила интеграции:

1. Подключение только как библиотека (pip dependency).
2. Версия фиксируется на tag (pinned), а не `main`.
3. В нашем коде создается отдельный adapter-layer, чтобы снизить зависимость от их internal API.
4. Этот репозиторий остается read-only reference в текущем проекте.

## Alternatives Considered

1. Писать собственный runtime с нуля.
2. Рендерить напрямую в чистый LangGraph без промежуточного framework.
3. Сразу поддерживать несколько runtime targets.

## Consequences

### Positive

1. Быстрый старт исполняемого MVP.
2. Переиспользование invoke/resume и node event модели.
3. Меньше рисков в начале проекта.

### Negative / Trade-offs

1. Риск несовместимости при апдейтах внешнего проекта.
2. Часть Python API у них помечена как internal.
3. Нужна дисциплина адаптерного слоя и pinning policy.

## Implementation Notes

1. Ввести модуль `optimizer.renderer.langgraph_dai`.
2. Ограничить импорт точками расширения: `BaseWorkflow`, `WorkflowNodeSpec`, model gateways/interfaces.
3. Добавить smoke tests на adapter при каждом обновлении pinned tag.

## Verification

1. Минимальный IR рендерится в исполняемый workflow.
2. Проходит invoke/resume сценарий.
3. Собираются node-level events для white-box трассировки.

## Links

1. `Roadmap.md` - I0.S1, I1, I2.
2. `README.md`.
3. `System_Architecture_Overview.md`.
