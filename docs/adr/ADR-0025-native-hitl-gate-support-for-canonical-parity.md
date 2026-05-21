# ADR-0025: Native HITL Gate Support for Canonical DSL->Native Parity

- Status: Accepted
- Date: 2026-05-21
- Slice: I4.S6a

## Context

Canonical stylizer profile включал участника с `hitl_gate` узлом (`human_review`).
Native runtime v0 не поддерживал `hitl_gate`, из-за чего canonical профиль блокировался preflight-ом.

## Decision

Принято расширить native exporter/runtime поддержкой `hitl_gate` без workaround policy:

1. `hitl_gate` добавлен в supported node kinds native export v0.
2. В native runtime добавлен executor `_execute_hitl_gate` с DSL-эквивалентной fallback-семантикой:
   - `review_decision` берется из payload,
   - default: `approve`.
3. Preflight capability matrix обновлена: `hitl_gate` считается supported.

## Consequences

Плюсы:

1. canonical stylizer profile запускается на native target без деградационных режимов.
2. Устранена корневая несовместимость по demo-critical пути.
3. Сохранен strict preflight для реально неподдержанных kind (например `tool`).

Ограничения:

1. Полное покрытие node kinds еще не закрыто (`tool` остается в `I4.S6`).
