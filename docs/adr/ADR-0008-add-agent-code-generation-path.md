# ADR-0008: Add Agent Code Generation Path

- Status: Accepted
- Date: 2026-05-06
- Slice: I2.S2
- Decision Makers: Project team
- Supersedes: N/A

## Context

После появления рабочего runtime-пути (`DSL -> IR -> invoke`) команда получила практический разрыв:
лучшая конфигурация после оценки существует как DSL/IR, но не как готовый кодовый артефакт, который можно сразу брать в прод-разработку.

Нужен ранний и воспроизводимый export-путь уже в MVP-1, без ожидания поздних evidence/export итераций.

## Decision

Добавить отдельный слайс `I2.S2` и внедрить `Agent Codegen v0`:

1. CLI генерации кода из `DSL` или `Graph IR`.
2. Генерация исполняемого Python-пакета агента + runner script.
3. Сохранение зафиксированного `graph_ir.json` внутри пакета.
4. Генерация `bindings.py` с безопасными fallback-обработчиками и TODO-точками для доменной доработки.

## Alternatives Considered

1. Отложить кодогенерацию до `I4.S3 Champion export bundle`.
2. Экспортировать только JSON/DSL без Python-кода.
3. Генерировать сразу полностью production-ready код без fallback-пути.

## Consequences

### Positive

1. Появился мост от оптимизации к внедрению: найденную конфигурацию можно запустить как код сразу.
2. Улучшился demo-story: теперь демонстрируется не только runtime, но и materialization артефакта.
3. Команда получает стандартную структуру артефакта для дальнейшего hardening.

### Negative / Trade-offs

1. Генерация v0 использует fallback-обработчики и требует ручного заполнения доменной логики.
2. Генератор пока не покрывает advanced-runtime функции (resume/checkpoint, full tracing).
3. Возникает дополнительный контур поддержки шаблонов codegen.

## Implementation Notes

1. Добавлен модуль `optimizer.codegen`:
   - `agent_generator.py`,
   - `generate.py`.
2. Добавлен smoke-сценарий:
   - `scripts/smoke_generate_agent_code.ps1`.
3. Добавлены тесты уровня unit/integration/e2e для codegen-пути.
4. Обновлены roadmap/backlog/demo документы для нового слайса и статусов.

## Verification

1. Unit: проверка генератора файлов и guard-логики перезаписи.
2. Integration: CLI codegen + запуск сгенерированного агента.
3. E2E: smoke script `DSL -> generate code -> run generated agent`.
4. Полный `python -m pytest` обязателен перед commit.

## Links

1. `docs/specs/Agent_Codegen_v0.md`
2. `Roadmap.md` (I2.S2)
3. `docs/demo/Demo_Track.md`

