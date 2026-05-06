# ADR-0010: Resume Checkpoint Contract Path v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I2.S4
- Decision Makers: Project team
- Supersedes: N/A

## Context

После I2.S3 есть node-level trace, но отсутствовал формализованный путь продолжения задач.
Для долгих и прерываемых execution-сценариев нужно:

1. сохранять checkpoint state по task_id;
2. возобновлять execution по task_id;
3. иметь проверяемые негативные контракты для missing/invalid task_id.

## Decision

Внедрить `Resume & Checkpoint Contract v0`:

1. Добавить файловый checkpoint-store runtime состояния.
2. Расширить runtime API методами `invoke` и `resume`.
3. Расширить CLI параметрами:
   - `--checkpoint-dir`
   - `--resume-task-id`
4. Использовать `task_id` как устойчивый идентификатор checkpoint thread.

## Alternatives Considered

1. Оставить только in-memory resume без checkpoint-store.
2. Делать resume исключительно через внешний сервисный слой.
3. Отложить resume до поздних MVP.

## Consequences

### Positive

1. Появился воспроизводимый `invoke -> resume` путь для демо и тестов.
2. Контракт task_id стал строгим и проверяемым.
3. Основа готова для перехода к persistent enterprise checkpoint backend.

### Negative / Trade-offs

1. v0 checkpoint-store файловый и локальный.
2. Нет cross-process distributed coordination.
3. Требуется последующее расширение для production-grade durability.

## Implementation Notes

1. Добавлен `FileRuntimeCheckpointStore`.
2. Обновлены runtime adapter/workflow/CLI.
3. Обновлены smoke-сценарии и integration tests.

## Verification

1. Integration: runtime invoke->resume с сохранением task_id.
2. Integration: CLI resume path.
3. Negative: empty/unknown task_id.
4. Полный `python -m pytest` зеленый.

## Links

1. `docs/specs/Resume_Checkpoint_Contract_v0.md`
2. `Roadmap.md` (I2.S4)
3. `docs/demo/Demo_Track.md`

