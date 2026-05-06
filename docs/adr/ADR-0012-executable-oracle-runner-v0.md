# ADR-0012: Executable Oracle Runner v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I3.S2
- Decision Makers: Project team
- Supersedes: N/A

## Context

После I3.S1 есть контракт датасета, но нет исполняемой проверки качества ответа.
Для reproducible оценки нужен runner, который дает pass/fail по кейсам и понятный summary.

## Decision

Принять `Oracle Runner v0`:

1. Ввести rule-contract `must_include/forbidden`.
2. Реализовать runner с подсчетом `cases_total/passed/failed/pass_rate`.
3. Добавить CLI `run_oracle`.
4. Ввести deterministic режим `expected_stub` как default для smoke/CI.

## Alternatives Considered

1. Сразу использовать только runtime LLM-оценку без deterministic режима.
2. Отложить oracle-runner до arena-слайса.
3. Хранить правила вне dataset expected-контракта.

## Consequences

### Positive

1. Появился исполняемый контур оценки на golden dataset.
2. Smoke и CI стабильны за счет deterministic `expected_stub`.
3. Подготовлена база для следующего arena-слайса.

### Negative / Trade-offs

1. Правила v0 простые и текстовые, без глубокой семантики.
2. Runtime-режим может быть недетерминированным при реальном LLM.
3. Контракт expected будет расширяться в следующих версиях.

## Implementation Notes

1. Добавлены `oracle_rules`, `oracle_runner`, `run_oracle`.
2. Добавлен smoke-script `smoke_run_oracle.ps1`.
3. Добавлены unit/integration/e2e тесты.

## Verification

1. Unit: проверка правил и подсчета runner.
2. Integration: CLI success/failure.
3. E2E: smoke oracle run.
4. Полный `python -m pytest` зеленый.

## Links

1. `docs/specs/Oracle_Runner_v0.md`
2. `Roadmap.md` (I3.S2)
3. `docs/demo/Demo_Track.md`

