# ADR-0013: Architecture Arena Equal-Budget Tournament v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I3.S3
- Decision Makers: Project team
- Supersedes: N/A

## Context

После I3.S2 есть исполняемая oracle-оценка одной архитектуры, но нет механизма
сравнить несколько кандидатных архитектур в одинаковых условиях и выбрать чемпиона.

Для MVP-1 нужен воспроизводимый baseline-турнир 2-3 кандидатов с прозрачным ранжированием.

## Decision

Принять `Architecture Arena v0`:

1. Ввести YAML-конфиг турнира (`arena_v0`) с 2-3 участниками.
2. Ввести equal-budget policy `equal_cases` (одинаковый набор кейсов для всех).
3. Реализовать CLI `run_tournament`.
4. Ввести deterministic demo-режим `expected_stub` с управляемым `stub_behavior`.
5. Выбирать чемпиона по прозрачному ranking contract.

## Alternatives Considered

1. Сравнивать только runtime-режим без deterministic профиля.
2. Оценивать участников по разным датасетам/разному числу кейсов.
3. Отложить arena до I4 вместе с evidence pack.

## Consequences

### Positive

1. Появился исполняемый и воспроизводимый турнир архитектур.
2. Появился понятный champion selection уже на MVP-1.
3. Демо-трек получил наглядный шаг сравнения 2-3 кандидатов.

### Negative / Trade-offs

1. `expected_stub` профили упрощают поведение и не равны production-качеству.
2. Метрика v0 сфокусирована на `pass_rate`, без cost/latency сигналов.
3. Полноценный multi-metric выбор чемпиона переносится в I4+.

## Implementation Notes

1. Добавлены `optimizer/arena/tournament_schema.py`, `io.py`, `runner.py`, `run_tournament.py`.
2. Добавлен demo-конфиг `examples/arena/support_tournament_v0.yaml`.
3. Добавлен smoke-script `scripts/smoke_run_arena.ps1`.
4. Добавлены unit/integration/e2e тесты arena-контура.

## Verification

1. Unit: ranking и equal-budget logic.
2. Integration: CLI success/failure.
3. E2E: smoke tournament run.
4. Полный `python -m pytest` зеленый.

## Links

1. `docs/specs/Architecture_Arena_v0.md`
2. `Roadmap.md` (I3.S3)
3. `docs/demo/Demo_Track.md`

