# ADR-0043: Target-stage-first Mapping and `stage_ref` Demotion

- Status: Accepted
- Date: 2026-05-29
- Slice: V2.4.S5b
- Decision Makers: Product + Engineering
- Supersedes: ADR-0040 (пункт 6, частично), V2.4.S5a UX-модель
- User Docs Page: docs/wiki/user_guides/c6-evaluators-matrix.md

## Context

После реализации `V2.4.S5a` выяснилось, что пользовательская модель стала избыточной:

1. В dataset уже есть `target_stage` (`final/synthesis/rerank/retrieval`), который задает смысл оценки.
2. Отдельный пользовательский `stage_ref` дублирует intent и добавляет лишнюю когнитивную нагрузку.
3. Пользователю важнее видеть, как система сопоставила stage с конкретными узлами каждого кандидата.

## Decision

Переходим на `target_stage-first` UX/contract:

1. Пользовательский stage-контракт: только `target_stage` из dataset.
2. Система строит mapping автоматически:
   - вход: `target_stage` + graph выбранных кандидатов,
   - выход: `candidate_id -> node_id(s)` + `confidence` + `reason`.
3. Пользователь может вручную скорректировать mapping per-candidate (manual override).
4. `stage_ref` убирается из основного UX и остается внутренним техническим слоем для replay/versioning/debug.

## Consequences

### Positive

1. Упрощается пользовательская модель (один stage source of truth).
2. Снижается число ручных шагов в C6.
3. Улучшается масштабирование на разные candidate-графы (mapping строится per-candidate).

### Negative / Trade-offs

1. Нужен migration path для уже сохраненных `stage_bindings`.
2. Усложняется внутренний mapping engine и его explainability surface.
3. Нужны дополнительные тесты на auto-map + manual override consistency.

## Implementation Notes (V2.4.S5b)

1. UI:
   - заменить `Stage bindings` на `Stage mapping`.
   - показывать mapping matrix по кандидатам и stage.
2. Backend:
   - добавить auto-map endpoint/handler на основе `target_stage`.
   - хранить override artifact отдельно от dataset rows.
3. Data model:
   - dataset rows не меняются (`target_stage` остается).
   - `stage_ref` переводится в internal-only поле/слой.
4. Validation:
   - preflight проверяет полноту mapping для включенных diagnostic signals.
5. Migration:
   - legacy `stage_bindings` конвертируются в mapping overrides без потери истории.

## Verification

1. Unit: auto-map heuristics + override precedence.
2. Integration: C6 API save/validate flow с mapping matrix.
3. Frontend: UI path `auto-map -> edit override -> save -> validate`.
4. E2E: выбранные кандидаты + non-final metrics проходят preflight без ручного `stage_ref`.
