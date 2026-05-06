# ADR-0007: Render Graph IR via LangGraph-DAI Workflow Adapter

- Status: Accepted
- Date: 2026-05-06
- Slice: I2.S1
- Decision Makers: Project team
- Supersedes: N/A

## Context

После реализации DSL->IR нужен исполняемый runtime-путь для демо и дальнейшей оптимизации.
Требования:

1. использовать `langgraph-dai` как первый runtime target;
2. поддерживать invoke path уже сейчас;
3. поддержать branch-условия и базовые failure policies;
4. иметь реальный LLM-путь через OpenRouter при наличии ключа.

## Decision

Реализован adapter `Graph IR -> RenderedGraphIRWorkflow`:

1. workflow строится поверх `framework.workflows.BaseWorkflow`;
2. узлы исполняются через `GraphIRNodeExecutor`;
3. branch-условия оцениваются `ConditionEvaluator`;
4. LLM узлы:
   - real OpenRouter call при `OPENROUTER_API_KEY`;
   - mock fallback без ключа.

## Alternatives Considered

1. Отложить runtime и идти сразу к метрикам/оценке.
2. Делать только mock-runtime без реальных LLM вызовов.
3. Прямой рендер в чистый LangGraph без layer adapter.

## Consequences

### Positive

1. Есть рабочий исполняемый путь для demo уже на I2.S1.
2. Реальные LLM-вызовы включаются конфигом без изменения кода.
3. Упрощается переход к I2.S2 (trace/events) и I3 (evaluation).

### Negative / Trade-offs

1. Branch-логика в v0 опирается на упрощенный condition evaluator.
2. MCP/tool интеграция пока в stub-режиме.
3. Нужна дисциплина тестов и demo-sync при развитии runtime.

## Implementation Notes

1. Добавлен пакет `optimizer.renderer.langgraph_dai`.
2. Добавлен CLI runtime runner и smoke demo script.
3. Добавлено покрытие unit/integration/e2e для рендерера.

## Verification

1. Полный `python -m pytest` зеленый.
2. Smoke runtime demo проходит.

## Links

1. `docs/specs/Renderer_LangGraphDAI_v0.md`
2. `Roadmap.md` (I2.S1)
3. `docs/demo/Demo_Track.md`
