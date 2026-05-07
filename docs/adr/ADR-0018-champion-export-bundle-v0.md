# ADR-0018: Champion Export Bundle v0

- Status: Accepted
- Date: 2026-05-08
- Slice: I4.S3
- Decision Makers: Project team
- Supersedes: N/A

## Context

После появления Architecture Arena и Evidence Pack у нас есть ranking и диагностика, но нет
единого deployable/reusable артефакта winner-кандидата.

Это создает проблемы:

1. сложно передать лучший кандидат в эксплуатацию без ручной сборки файлов;
2. теряется связка `winner config -> evidence -> diagnostic interventions`;
3. нет стандартного handoff-пакета для следующего optimization-цикла.

## Decision

Вводим `Champion Export Bundle v0` как обязательный экспортный артефакт после выбора winner:

1. Добавляем CLI:
   - `python -m optimizer.champion.export_bundle`.
2. Bundle содержит:
   - `arena_result.json`,
   - `evidence_pack.json` + `evidence_pack.md`,
   - `diagnostic_map.json`,
   - `winner_graph_ir.json`,
   - `winner_source/*`,
   - `generated_agent/*`,
   - `bundle_manifest.json`.
3. `diagnostic_map.json` формируется как приоритизированный список точек оптимизации:
   - по winner bottlenecks,
   - по fallback наблюдению stage,
   - по cross-metric gap из comparison diff.

## Alternatives Considered

1. Оставить только `evidence_pack` без экспортного bundle.
2. Экспортировать только DSL/IR winner без runnable code.
3. Экспортировать только код, без diagnostics/evidence контекста.

## Consequences

### Positive

1. Есть единый handoff-пакет winner для команды и для CI/CD контура.
2. Диагностика и рекомендации не теряются между итерациями.
3. Новый разработчик видит полный контекст winner в одном каталоге.

### Negative / Trade-offs

1. Увеличивается объем артефактов и время экспорта.
2. Нужна синхронная поддержка форматов bundle/evidence/arena.

## Implementation Notes

1. Добавлен модуль `optimizer/champion`:
   - `diagnostic_map.py`,
   - `export_bundle.py`.
2. Добавлен smoke-скрипт:
   - `scripts/smoke_export_champion_bundle.ps1`.
3. Добавлено тестовое покрытие:
   - unit/integration/e2e.

## Verification

1. `python -m pytest` проходит green.
2. CLI формирует bundle-каталог с manifest и обязательными файлами.
3. `diagnostic_map.json` содержит `top_optimization_points` с приоритетами.

## Links

1. `docs/specs/Champion_Export_Bundle_v0.md`
2. `optimizer/champion/export_bundle.py`
3. `optimizer/champion/diagnostic_map.py`

