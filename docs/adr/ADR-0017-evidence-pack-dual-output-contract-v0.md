# ADR-0017: Evidence Pack Dual Output Contract v0

- Status: Accepted
- Date: 2026-05-07
- Slice: I4.S2
- Decision Makers: Project team
- Supersedes: N/A

## Context

После появления dual-модели метрик (`comparison` vs `diagnostics`) в arena-выводе не хватает отдельного артефакта,
который:

1. фиксирует winner/challenger сравнение в explainable форме;
2. отделяет ranking-метрики от root-cause диагностики;
3. удобен как для автоматических пайплайнов, так и для ручного review.

## Decision

Вводим `Evidence Pack v0` как обязательный артефакт после tournament run:

1. Формат артефактов:
   - `evidence_pack.json`,
   - `evidence_pack.md`.
2. Контракт строго разделяет:
   - `comparison`,
   - `diagnostics`.
3. Добавляем `winner_vs_challenger_diff` с интерпретацией по направлению метрик (`asc|desc`).
4. Добавляем `recommendations.for_challenger_priority_actions` на базе diff + diagnostics hints.

## Alternatives Considered

1. Оставить только сырой arena JSON без дополнительного пакета.
2. Делать только markdown-отчет без структурированного json.
3. Смешивать comparative и diagnostic сигналы в одном агрегированном score.

## Consequences

### Positive

1. Проще объяснять, почему winner выбран корректно.
2. Появляется воспроизводимый вход для следующего optimization-шага.
3. Новому разработчику легче понять текущее состояние и план intervention.

### Negative / Trade-offs

1. Дополнительный слой генерации артефактов и тестового покрытия.
2. Нужно синхронно поддерживать контракт arena и contract evidence pack.

## Implementation Notes

1. Добавлен модуль `optimizer/evidence`.
2. Добавлен CLI `python -m optimizer.evidence.generate_pack`.
3. Добавлен smoke-скрипт `scripts/smoke_generate_evidence_pack.ps1`.
4. Добавлены unit/integration/e2e тесты evidence pack.

## Verification

1. `python -m pytest` проходит green.
2. CLI формирует `evidence_pack.json` и `evidence_pack.md`.
3. В output присутствуют `comparison`, `diagnostics`, `winner_vs_challenger_diff`.

## Links

1. `docs/specs/Evidence_Pack_v0.md`
2. `optimizer/evidence/pack_builder.py`
3. `optimizer/evidence/generate_pack.py`

