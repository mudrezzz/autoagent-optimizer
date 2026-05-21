# ADR-0028: Native-First Champion Bundle Default

- Status: Accepted
- Date: 2026-05-22
- Slice: I4.S8
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: N/A

## Context

После I4.S7 мы доказали структурный parity между DSL-path и native exported path, но champion bundle по контракту все еще выглядел как dual-entry без явного default target. Это оставляло неоднозначность:

1. какой runtime считать production-first при handoff;
2. как быстро запускать winner без чтения внутренних договоренностей;
3. как зафиксировать generated path только как debug fallback, а не основной execution path.

## Decision

Фиксируем `native_runtime` как default runtime target в champion bundle v0:

1. в `bundle_manifest.json` добавляются поля:
   - `default_runtime_target`,
   - `default_entrypoint_file`,
   - `legacy_debug_entrypoint_file`;
2. CLI success payload возвращает те же default/debug поля;
3. `README.bundle.md` рендерится в native-first порядке:
   - сначала standalone native запуск,
   - затем generated debug fallback.

## Alternatives Considered

1. Сохранить dual-entry без default policy.
2. Сделать generated path default и native path optional.
3. Удалить generated path полностью.

## Consequences

### Positive

1. Handoff становится однозначным: winner запускается через native entrypoint по умолчанию.
2. Снижается риск случайного использования legacy runtime как production path.
3. Debug-возможность сохраняется без блокировки миграции на native-first.

### Negative / Trade-offs

1. Появляется новый контрактный слой (default/debug поля), который нужно поддерживать в тестах и документации.
2. Старые внешние скрипты, ориентированные только на generated entrypoint, должны читать обновленный manifest.

## Implementation Notes

Изменения ограничены контуром champion export:

1. `optimizer/champion/export_bundle.py` (manifest + CLI payload + README.bundle layout);
2. `tests/integration/test_champion_export_bundle_cli.py` (проверка новых контрактных полей);
3. спецификация `docs/specs/Champion_Export_Bundle_v0.md` и статусные документы (`Roadmap`, `README`, backlog/demo snapshot).

## Verification

1. Полный `python -m pytest` (unit + integration + e2e) после слайса.
2. Интеграционный тест champion export проверяет:
   - `default_runtime_target == native_runtime`,
   - существование `default_entrypoint_file`,
   - существование `legacy_debug_entrypoint_file`.

## Links

1. Roadmap slice: `I4.S8`.
2. Spec: `docs/specs/Champion_Export_Bundle_v0.md`.
