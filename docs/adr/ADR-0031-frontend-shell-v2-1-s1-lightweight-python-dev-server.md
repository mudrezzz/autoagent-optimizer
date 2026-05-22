# ADR-0031: Frontend Shell V2.1.S1 via Lightweight Python Dev Server

- Status: Accepted
- Date: 2026-05-22
- Slice: V2.1.S1
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: N/A

## Context

Для `V2.1.S1` нужно было быстро получить проверяемый frontend shell `C1..C6` с минимум одним реальным backend-вызовом
и не ломать текущий python-first контур проекта.

На момент слайса в репозитории не было готового frontend framework/runtime и web API gateway.

## Decision

Принимаем lightweight подход для bootstrap:

1. frontend shell реализуется как статический `frontend/` пакет;
2. delivery API реализуется в `optimizer.frontend.dev_server` на `ThreadingHTTPServer` (stdlib);
3. endpoint `POST /api/c1/validate-compile` подключается к реальному DSL validate+compile path;
4. endpoints `GET /api/c2..c6/sample` остаются stub до следующих vertical slices.

## Alternatives Considered

1. Сразу поднимать полноценный frontend framework + отдельный backend web stack.
2. Оставить только статический UI без API и без реального backend вызова.
3. Реализовать только API без UI shell.

## Consequences

### Positive

1. Быстрый старт вертикального frontend delivery без внешних зависимостей.
2. Реальный C1 path уже проверяется через UI + integration/e2e тесты.
3. Низкий порог входа для команды (запуск одной python-командой).

### Negative / Trade-offs

1. Dev server не является production-grade web stack.
2. Для дальнейшего роста может потребоваться миграция на более зрелую frontend/backend web-платформу.
3. Stub endpoints нужно последовательно заменять реальными реализациями в V2.1.S2+.

## Implementation Notes

1. Добавлены `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`, `frontend/README.md`.
2. Добавлен `optimizer/frontend/contracts.py` и `optimizer/frontend/dev_server.py`.
3. Добавлены smoke/integration/e2e проверки frontend shell.
4. Обновлены roadmap/backlog/demo/README статусы по `V2.1.S1`.

## Verification

1. Unit: `tests/unit/test_frontend_contracts.py`.
2. Integration: `tests/integration/test_frontend_dev_server.py`.
3. E2E: `tests/e2e/test_frontend_shell_smoke_script.py` + `scripts/smoke_frontend_shell.ps1`.
4. Full gate: `python -m pytest`.

## Links

1. `frontend/README.md`
2. `optimizer/frontend/dev_server.py`
3. `Roadmap.md` (`V2.1.S1` status).
