# ADR-0016: Dual Metrics Model - Comparative Vs Diagnostic

- Status: Accepted
- Date: 2026-05-07
- Slice: I4.S2 (planning baseline)
- Decision Makers: Project team
- Supersedes: None

## Context

После внедрения `middle_metrics` стало ясно, что под этим термином смешиваются две разные цели:

1. Межархитектурное сравнение (кто лучше в турнире).
2. Поиск точки поломки внутри конкретного пайплайна (что чинить в первую очередь).

Если смешивать эти цели в одном наборе метрик, оптимизатор теряет фокус:
ranking перестает быть прозрачным, а диагностика становится шумной.

## Decision

Принята dual-metrics модель с жестким разделением:

1. `Comparative Metrics`:
   - используются только для ranking/tournament selection;
   - формируют `composite_score`;
   - должны быть сопоставимы между разными архитектурами.
2. `Diagnostic Signals`:
   - используются только для root-cause анализа и intervention planning;
   - считаются на уровне `case -> stage/node -> aggregate`;
   - не участвуют напрямую в глобальном ranking.

Дополнительно:

1. Для диагностики вводится stage taxonomy (`retrieve`, `rerank`, `synthesize`, `validate`, `tool_call`, `hitl`, ...).
2. Для приоритизации улучшений применяется `bottleneck_score` (impact * prevalence * confidence / fix_cost).
3. Evidence Pack должен публиковать отдельные секции:
   - `comparison`
   - `diagnostics`.

## Consequences

### Positive

1. Ranking и локальная диагностика перестают конфликтовать по целям.
2. Появляется системный путь от наблюдения к intervention operators.
3. Повышается explainability: "почему победил" и "что чинить" разделены явно.

### Negative / Trade-offs

1. Усложняется контракт отчетов и объем данных.
2. Потребуется унификация stage taxonomy для гетерогенных графов.
3. На первом этапе часть diagnostic checks будет эвристической.

## Verification

1. Contract tests на разделение `comparison` и `diagnostics`.
2. Integration tests на построение diagnostic sections в Evidence Pack.
3. E2E smoke, показывающий хотя бы один приоритизированный bottleneck.

## Links

1. `Roadmap.md` (I4.S2, I6.S3)
2. `docs/backlog/Executable_Slice_Backlog.md`
3. `System_Architecture_Overview.md`
