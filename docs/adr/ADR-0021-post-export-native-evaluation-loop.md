# ADR-0021: Post-export Native Evaluation Loop

- Status: Accepted
- Date: 2026-05-09
- Slice: I5.S4 (design)
- Decision Makers: Project team
- Supersedes: N/A

## Context

После выбора winner и экспорта `native_agent` цикл улучшений не должен обрываться.
Нужен системный способ:

1. прогонять exported native agent по тем же (или новым) benchmark-профилям;
2. сравнивать с baseline winner и фиксировать regression;
3. поддерживать semi-white-box наблюдаемость после ручных правок native-агента.

## Decision

Вводим `post-export native evaluation loop` как часть основного roadmap:

1. Exported native agent становится полноценным execution target для evaluation fabric.
2. Evaluation Profile описывает:
   - какие метрики/сигналы считаем,
   - какие evaluator adapters используем (`golden`, `llm_judge`, `executable`, ...),
   - какие regression gates применяем.
3. Champion lifecycle расширяется:
   - `export -> benchmark native -> compare with baseline -> promote/rework`.

## Alternatives Considered

1. Оставить post-export проверку ad-hoc скриптами.
2. Оценивать только DSL-runtime и считать native-экспорт “доверенным”.
3. Делать только manual review без автоматических regression gates.

## Consequences

### Positive

1. Цикл оптимизации не прерывается после экспорта.
2. Любые ручные правки native-агента проверяются единым benchmark-контуром.
3. Появляется формализованный promote/reject процесс для champion revisions.

### Negative / Trade-offs

1. Усложняется evaluation fabric (execution-target adapters + gate orchestration).
2. Увеличивается стоимость прогонов (особенно с `llm_judge`).
3. Нужны reproducibility controls (versioned profiles, manifests, seeds).

## Implementation Notes

1. Интегрировать в I5:
   - I5.S1: profile contract с execution targets,
   - I5.S2: native runtime evaluator adapter,
   - I5.S4: post-export benchmark loop,
   - I5.S5: regression gates.
2. Демо-трек должен включать “native champion re-benchmark after edit”.

## Verification

1. Exported native agent запускается через evaluator adapters в общем benchmark pipeline.
2. Отчет включает comparative + diagnostic + regression секции.
3. Gate policy блокирует promotion при выходе за пороги regression.

## Links

1. `docs/specs/Post_Export_Evaluation_Loop_v0.md`
2. `Roadmap.md` (I5.S1-I5.S5)
3. `docs/backlog/Executable_Slice_Backlog.md`

