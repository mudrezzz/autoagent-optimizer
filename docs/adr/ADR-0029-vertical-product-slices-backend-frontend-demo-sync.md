# ADR-0029: Vertical Product Slices with Backend-Frontend-Demo Sync

- Status: Accepted
- Date: 2026-05-22
- Slice: V2.1.S1
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: N/A

## Context

По мере усложнения backend-only трека стало тяжелее оценивать прогресс и корректность реализации:

1. функциональность на backend появлялась быстрее, чем становилась проверяемой пользователем;
2. демо отставало и не давало раннего сигнала о проблемах UX/API стыка;
3. команда теряла нить при последовательном развитии глубины одного направления.

Нужен режим, где продуктовые capability развиваются вширь и подтверждаются через UI на каждом шаге.

## Decision

Фиксируем переход на вертикальный delivery mode (`Roadmap v2`):

1. каждый слайс обязан включать `Backend + Frontend + Demo + QA`;
2. разработка идет capability-first (C1..C6), а не только layer-first;
3. backend-инкремент считается незавершенным, пока не имеет frontend surface и e2e-проверку;
4. ближайшее окно планирования переключается на смешанные итерации `V2.1` и `V2.2`.

## Alternatives Considered

1. Оставить последовательный backend-first порядок и добавлять UI в конце итерации.
2. Развивать frontend отдельной длинной фазой после закрытия I5.
3. Поддерживать только CLI/demo без полноценного frontend контура.

## Consequences

### Positive

1. Быстрее выявляются ошибки на стыке API/UX.
2. Прогресс становится проверяемым для всей команды и стейкхолдеров.
3. Снижается риск накопления неподтвержденной backend-сложности.

### Negative / Trade-offs

1. Увеличивается координационная нагрузка в каждом слайсе.
2. Нужна дисциплина синхронизации документации и capability board.
3. Некоторые backend задачи будут выполняться чуть медленнее из-за обязательного UI/e2e контура.

## Implementation Notes

1. Обновить `Roadmap.md`:
   - capability matrix C1..C6,
   - вертикальные итерации `V2.1` и `V2.2`.
2. Обновить `Executable_Slice_Backlog.md`:
   - active next slice -> `V2.1.S1`,
   - near-term vertical iteration plan.
3. Обновить `Demo_Track.md`:
   - stage `D4.5` для capability-first frontend demo.
4. Обновить `Project_Operating_Model.md` и `README.md`:
   - вертикальный DoD и правила синхронизации.

## Verification

1. Для каждого нового слайса проверяется 4-осевая готовность: `BE / FE / Demo / QA`.
2. В PR/commit описании фиксируется, какой frontend surface добавлен.
3. Обязательный полный прогон `python -m pytest` сохраняется.

## Links

1. `Roadmap.md` (`Execution Shift (Roadmap v2)`, `V2.1`, `V2.2`).
2. `docs/backlog/Executable_Slice_Backlog.md` (active window V2).
3. `docs/demo/Demo_Track.md` (`Stage D4.5`).
