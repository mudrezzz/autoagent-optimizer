# ADR-0024: Reject Native Degradation Workaround, Prioritize DSL==Native Parity

- Status: Accepted
- Date: 2026-05-20
- Slice: Planning update after I5.S2a

## Context

После внедрения native preflight (`I5.S2a`) обсуждался путь `skip_unsupported`,
чтобы частично запускать native profile при несовместимых participants.

Риск этого пути:

1. результат сравнения становится неполным и может вводить в заблуждение,
2. команда тратит время на обходной контур вместо устранения корневой несовместимости,
3. растет технический долг в evaluation/reporting контрактах.

## Decision

Принято:

1. не реализовывать `I5.S2b` как product-функциональность,
2. зафиксировать `I5.S2b` как rejected workaround в backlog,
3. сместить следующий активный слайс на `I4.S6a`:
   - добиться прохождения canonical stylizer profile на native runtime,
   - выровнять семантику DSL и native без деградационных политик.

## Consequences

Плюсы:

1. фокус на сутевом качестве платформы (`DSL == Native`),
2. меньше обходных режимов и спорных интерпретаций результатов,
3. чище дальнейший путь к CI parity gate и champion native-first.

Минусы:

1. краткосрочно меньше “быстрых” запусков при частичной несовместимости,
2. требуется более глубокая работа в runtime bindings раньше по плану.
